# RevBusinessCardGen
Easily Generate Revolut Business Cards

## Prerequisites

Before you begin, ensure you have met the following requirements:
- You have installed Python 3.7 or 3.8 

## QuickStart
  
  - Fill `config.py`
  ```bash
  >> pip install -r requirements.txt
  >> python gen.py
  ```
  
 ## Config
 
- `REV_TOKEN` # Get it after logging in revolut by looking in cookies, find `token` and copy paste the value
- `DEVICE_ID` = "" # Get it after logging in revolut by looking in a random request, find `x-device-id` in request headers, is the last one
- `GEN_NUMBER` = 200 # Input the number of cards you want to gen
- `EMPLOYEE_EMAIL` = "" # Input the email of the user you want to gen cards with
- `CARD_PREFIX` = "CARD_" # Input a string that will be in the card name (card names will be `{CARD_PREFIX}_1,{CARD_PREFIX}_2,...`


## Troubleshooting

- This action is forbidden returned means you have to refresh the token cookie



## Device Id Request

![image](https://user-images.githubusercontent.com/42220507/150025784-35791720-ed74-4eda-af5f-a862cf9bd75f.png)



 
