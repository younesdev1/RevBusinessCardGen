import datetime
import requests
import json
import config
import uuid
import traceback
from logging import info, error, basicConfig, INFO, ERROR


class RevGen:
    
    def __init__(self) -> None:
        
        
        self.headers_post =  {
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
            'accept': 'application/json, text/plain, /',
            'sec-ch-ua-mobile': '?0',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
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
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36',
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

        
              
        self.business_id = self.get_business()
        if not self.business_id:
            raise RuntimeError("Cannot Get Business API")
        if self.kyc_status != "PASSED":
            raise RuntimeError("Account Unverified")
        
        self.BASE_URL = config.BASE_URL + f"business/{self.business_id}"
        
        self.get_members()
        
        for n in range(0, int(config.GEN_NUMBER)):
            self.log_info(f"Generating Card {n}")
            self.gen_cards()
            self.log_info(f"Generated Card {n}")
            labeled = self.label_cards(n)
            if labeled:
                self.log_info(f"Labeled Card {n}")



                
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
        
        response = self.s.patch(
            f'{self.BASE_URL}/card/{self.card_id}/label',
            headers=self.headers_post,
            json=payload
            )
        
        try:
            return response.json()["state"] == "ACTIVE"
        except:
            self.log_error(f"Error Parsing API: {response.status_code} - {response.text} - {traceback.format_exc()}")           
        


if __name__ == "__main__":
    pass

RevGen()
        
            
                 
        
        
        
            