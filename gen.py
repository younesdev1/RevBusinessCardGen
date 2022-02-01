import datetime
import requests
import json
import config
import uuid
import traceback
from logging import info, error, basicConfig, INFO, ERROR
from datetime import date
import csv
import time
import pathlib

class RevGen:
    
    def __init__(self) -> None:
        
        
        self.ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36"
        
        self.headers_post =  {
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
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
            'cookie': f'token={config.REV_TOKEN}',
        }
        
        self.headers_get = {
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
        }

        
        
        self.s = requests.Session()
        self.csv_location = f'{pathlib.Path(__file__).parent.resolve()}\\cards.csv'
        

        
              
        self.business_id = self.get_business()
        if not self.business_id:
            raise RuntimeError("Cannot Get Business API")
        if self.kyc_status != "PASSED":
            raise RuntimeError("Account Unverified")
        
        self.BASE_URL = config.BASE_URL + f"business/{self.business_id}"
        
        self.get_members()
        
        for n in range(0, int(config.GEN_NUMBER)):
            self.log_info(f"Generating Card {n+config.START_WITH_INDEX}")
            self.gen_cards()
            self.log_info(f"Generated Card {n+config.START_WITH_INDEX}")
            labeled = self.label_cards(n+config.START_WITH_INDEX)
            if labeled:
                self.log_info(f"Labeled Card {n+config.START_WITH_INDEX}")
                if config.SMS_VERIFICATION:
                    self.get_card_details()
                    
        


                
    @staticmethod
    def log_info(*args, **kwargs):
        
        timestamp = datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]
        st,en = '\033[92m','\033[0m'
        output =  f"{st}[{str(timestamp)}] {args[0]}{en}"
        basicConfig(format="%(message)s", level=INFO)
        info(output)  
        
        
    @staticmethod
    def log_error(*args, **kwargs):
        st,en = '\033[91m','\033[0m'
        timestamp = datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]
        output =  f"{st}[{str(timestamp)}] {args[0]}{en}"
        basicConfig(format="%(message)s", level=ERROR)
        error(output)  
                      
        
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
            self.card_exp_month = f'0{str(date.today().month)}'
            self.card_exp_year = str(date.today().year + 5)
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
        
            
                 
        
        
        
            