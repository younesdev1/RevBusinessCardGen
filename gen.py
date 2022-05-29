import datetime
import config
import traceback
from logging import info, error, basicConfig, INFO, ERROR
from datetime import date
import time
import pathlib
import uuid
import cloudscraper
import os

class RevGen:
    
    def __init__(self) -> None:
        
        
        self.ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36"
        if config.DEVICE_ID == "":
            config.DEVICE_ID = str(uuid.uuid4())
        
        self.headers_post =  {
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="101", "Google Chrome";v="101"',
            'accept': 'application/json, text/plain, /',
            'sec-ch-ua-mobile': '?0',
            'user-agent': self.ua,
            'x-device-id': config.DEVICE_ID,
            'content-type': 'application/json;charset=UTF-8',
            'origin': 'https://business.revolut.com/',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://business.revolut.com/',
            'accept-language': 'en-US;q=0.9',
        }
        
        self.headers_get = {
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="101", "Google Chrome";v="101"',
            'accept': 'application/json, text/plain, */*',
            'sec-ch-ua-mobile': '?0',
            'user-agent': self.ua,
            'x-device-id': config.DEVICE_ID,
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://business.revolut.com/',
            'accept-language': 'en-US;q=0.9',
        }

        self.s = cloudscraper.create_scraper(requestPreHook=self.pre_hook)
        self.csv_location = f'{pathlib.Path(__file__).parent.resolve()}\\cards.csv'
        
        if config.EMAIL == "" or config.PASSWORD == "" and config.REV_TOKEN == "":
            raise RuntimeError("Email and Password or Rev Token are empty, supply at least one")
        
        if config.EMAIL != "" and config.PASSWORD != "":
            self.login()  
                
        self.business_id = self.get_business()
        if not self.business_id:
            raise RuntimeError("Cannot Get Business API")
        if self.kyc_status != "PASSED":
            raise RuntimeError("Account Unverified")
        
        self.BASE_URL = config.BASE_URL + f"business/{self.business_id}"
        
        self.get_members()
        
        for n in range(0, int(config.GEN_NUMBER)):
            if not config.COPY_ONLY:
                self.log_info(f"Generating Card {n+config.START_WITH_INDEX}")
                self.gen_cards()
                self.log_info(f"Generated Card {n+config.START_WITH_INDEX}")
                labeled = self.label_cards(n+config.START_WITH_INDEX)
                if labeled:
                    self.log_info(f"Labeled Card {n+config.START_WITH_INDEX}")
                    self.card_exp_month = f'0{str(date.today().month)}'
                    self.card_exp_year = str(date.today().year + 5)
                if config.SMS_VERIFICATION:
                    self.get_card_details()
            else:
                self.get_all_cards()
                for key,value in self.cards.items():
                    self.card_id = key
                    self.card_name = value["name"]
                    self.card_exp_month = value["expiryDate"].split("/")[0]
                    self.card_exp_year = value["expiryDate"].split("/")[1]
                    self.log_info(f"Retrieved Card {self.card_name}")
                    if config.SMS_VERIFICATION:
                        self.get_card_details()
                    
        
    def pre_hook(self, request, method, url, *args, **kwargs):
        if hasattr(self,"expires"):
            if self.expires < time.time():
                self.login()
        if not self.s.cookies.get("token", None) and config.REV_TOKEN != "":
            self.s.cookies["token"] = config.REV_TOKEN
            
        return method, url, args, kwargs
        

                
    @staticmethod
    def log_info(*args, **kwargs):
        os.system("")
        timestamp = datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]
        st,en = '\033[92m','\033[0m '
        output =  f"{st}[{str(timestamp)}] {args[0]}{en}"
        basicConfig(format="%(message)s", level=INFO)
        info(output)  
        
        
    @staticmethod
    def log_error(*args, **kwargs):
        os.system("")
        st,en = '\033[91m','\033[0m '
        timestamp = datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]
        output =  f"{st}[{str(timestamp)}] {args[0]}{en}"
        basicConfig(format="%(message)s", level=ERROR)
        error(output)  
                      
    def login(self):
        
        self.log_info(f"Logging in")
        
        json_data = {
            'email': config.EMAIL,
            'password': config.PASSWORD
        }

        response = self.s.post(
            'https://business.revolut.com/api/signin',
            headers=self.headers_post,
            json=json_data
        )        
        try:
            parsed = response.json()
            config.REV_TOKEN = self.s.cookies["token"]
        except:
            RuntimeError(f"Error Parsing API: {response.status_code} - {response.text}")
                    
        if "userId" not in parsed:
            raise RuntimeError(f"Cannot Login: {parsed}")
        
        response = self.s.post('https://business.revolut.com/api/2fa/signin/verify', headers=self.headers_post)
        try:
            parsed = response.json()
            verification_token = parsed["verificationTokenId"]
        except:
            raise RuntimeError(f"Error Parsing API: {response.status_code} - {response.text}")
        
        response = self.s.get(f'https://business.revolut.com/api/verification/{verification_token}/status', headers=self.headers_get)
        parsed = response.json() 
        
        while parsed["state"] != "VERIFIED":
            self.log_info(f"Waiting for App confirmation")
            time.sleep(2)
            response = self.s.get(f'https://business.revolut.com/api/verification/{verification_token}/status', headers=self.headers_get)
            parsed = response.json() 
            
        code = parsed["code"]
        headers = self.headers_post.copy()
        headers["x-verify-code"] = code
        
        verify = self.s.post('https://business.revolut.com/api/2fa/signin/verify', headers=headers)
        try:
            parsed = verify.json()
            self.expires = parsed["expireAt"]
            config.REV_TOKEN = self.s.cookies["token"]
        except:
            raise RuntimeError(f"Error Parsing API: {response.status_code} - {response.text}")        

        
    def get_business(self):
        self.log_info("Getting Business")
        
        response = self.s.get(
            config.CURRENT_USER,
            headers=self.headers_get
            )
        
        if "This action is forbidden" in response.text:
            raise RuntimeError("Token Expired")
        
        try:
            parsed = response.json()

            self.kyc_status = parsed["kyc"]
            business_id = parsed["businessId"]
            return business_id
        except:
            self.log_error(f"Error Parsing API: {response.status_code} - {response.text} - {traceback.format_exc()}")
            
    
    def get_members(self):

        self.log_info("Getting Team Members")
        
        response = self.s.get(
            f"{self.BASE_URL}/team/members",
            headers=self.headers_get
        )
        
        if "This action is forbidden" in response.text:
            raise RuntimeError("Token Expired")
        
        try:
            parsed = response.json()
            self.current_member = [m for m in parsed if m["email"] == config.EMPLOYEE_EMAIL][0]
            try:
                self.employee_id = self.current_member["employee"]["id"]
            except:
                self.employee_id = ""
                
            self.user_id = self.current_member["user"]["id"]

        except:
            self.log_error(f"Error Parsing API: {response.status_code} - {response.text} - {traceback.format_exc()}")   
            
    def get_all_cards(self):
        
        response = self.s.get(
            f'{self.BASE_URL}/team/members/current-member/cards',
            headers=self.headers_get
        )
        
        if "This action is forbidden" in response.text:
            raise RuntimeError("Token Expired")
        
        try:
            self.cards = {}
            parsed = response.json()
            for x in parsed:
                self.cards[x["payload"]["id"]] = {
                    "name": x["payload"]["name"], 
                    "expiryDate": x["payload"]["expiryDate"],
                }
            self.user_id = self.current_member["user"]["id"]
        except:
            self.log_error(f"Error Parsing API: {response.status_code} - {response.text} - {traceback.format_exc()}")           
    
    def gen_cards(self):
        
        payload = {
            "includedToExpenseManagement":True,
            "linkAllAccounts":True,
            "email": config.EMPLOYEE_EMAIL,
            "employeeId": self.employee_id,
            "userId": self.user_id,
            "personal":True
        }
        
        response = self.s.post(
            f'{self.BASE_URL}/card/virtual/order',
            headers=self.headers_post,
            json=payload
        )
        
        if "This action is forbidden" in response.text:

            raise RuntimeError("Token Expired")
        
          
        try:
            self.card_id = response.json()["id"]
        except:
            self.log_error(f"Error Parsing API: {response.status_code} - {response.text} - {traceback.format_exc()}")   
        
    
    def label_cards(self, prefix):
        
        self.log_info("Labeling Card")   
        
        payload = {"label": f"{config.CARD_PREFIX} {prefix}"} 

        self.card_name = f"{config.CARD_PREFIX}{prefix}"

        response = self.s.patch(
            f'{self.BASE_URL}/card/{self.card_id}/label',
            headers=self.headers_post,
            json=payload
            )
        
        try:
            return response.json()["state"] == "ACTIVE"
        except:
            self.log_error(f"Error Parsing API: {response.status_code} - {response.text} - {traceback.format_exc()}") 
            
            
    def send_sms(self):
        resp_code = 'resp'
        print(f'[{self.card_name}] Sending SMS...')
        while not '"Verification required","code":9014,"factor":"SMS"' in resp_code:
            response = self.s.get(
                f"{self.BASE_URL}/card/{self.card_id}/image/unmasked?encrypt=false",
                headers=self.headers_get
            )
            resp_code = response.text
            if '"Cannot create a new verification code at that moment","code":9015' in resp_code:
                print(f'[{self.card_name}] Error sending SMS waiting 5 seconds...')
                time.sleep(5)

        print(f'[{self.card_name}] SMS code sent')


    def get_card_details(self):
        self.send_sms()
        Resend = True
        while Resend:
            self.sms_code = input(f'[{self.card_name}] Enter sms code (type "1" to send sms again): ') 
            if self.sms_code == "1":
                self.send_sms()  
            else:
                Resend = False

        self.verify_headers = {
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'sec-ch-ua': '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
            'accept': 'application/json, text/plain, */*',
            'sec-ch-ua-mobile': '?0',
            'user-agent': self.ua,
            'x-device-id': config.DEVICE_ID,
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://business.revolut.com/',
            'accept-language': 'en-US;q=0.9',
            'cookie': f'token={config.REV_TOKEN}', 
            'x-verify-code': f'{self.sms_code}',
        }
        response = self.s.get(
            f"{self.BASE_URL}/card/{self.card_id}/image/unmasked?encrypt=false",
            headers=self.verify_headers
        )
        try:
            self.card_num = response.json()["pan"]
            self.card_cvv = response.json()["cvv"]
            self.write_card_details()
        except:
            choice = input(f'[{self.card_name}] Wrong sms code wanna try again? y/n: ')
            if choice == "y":
                self.get_card_details()
            else:
                return
        


    def write_card_details(self):
        with open(self.csv_location, 'a') as fd:
            fd.write(f'\n{self.card_name},{self.card_num},{self.card_exp_month},{self.card_exp_year},{self.card_cvv}')

if __name__ == "__main__":
    pass

RevGen()
        
            
                 
        
        
        
            