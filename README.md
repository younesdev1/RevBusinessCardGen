# RevBusinessCardGen
Easily Generate And Save Revolut Business Cards

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

- `EMAIL` # Your login email
- `PASSWORD` # Your login password

- `REV_TOKEN` # Get it after logging in revolut by looking in cookies, find `token` and copy paste the value (no need to supply if email & password are filled)
- `DEVICE_ID` = "" # Get it after logging in revolut by looking in a random request, find `x-device-id` in request headers, is the last one (no need to supply if email & password are filled)
- `COPY_ONLY` # Fill `True` if you want the script only to copy existing cards instead of genning too.
- `GEN_NUMBER` = 200 # Input the number of cards you want to gen
- `EMPLOYEE_EMAIL` = "" # Input the email of the user you want to gen cards with
- `CARD_PREFIX` = "CARD_" # Input a string that will be in the card name (card names will be `{CARD_PREFIX}_1,{CARD_PREFIX}_2,...`
- `START_WITH_INDEX` = 0 # INDEX WITH YOU WANT TO START CREATING YOUR CARD / COPYING YOUR CARDS EX. (44) {CARD_PREFIX}_44, {CARD_PREFIX}_45...
- `SMS_VERIFICATION` #Use True if you want to confirm sms code and store card information in "cards.csv"

## Notes  
If you're trying to copy from a specific index, put the index number where it stopped - 1. Like if it stopped writing details on csv on card 5, to start copying again from 5 you should input 4.

## Troubleshooting

- This action is forbidden returned means you have to refresh the token cookie  


## Device Id Request

![image](https://user-images.githubusercontent.com/42220507/150025784-35791720-ed74-4eda-af5f-a862cf9bd75f.png)



 
