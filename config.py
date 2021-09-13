REV_TOKEN =  ""  #COOKIES (Token)
DEVICE_ID = "" #x-device-id, all requests
GEN_NUMBER = 200 #HOW MANY CARDS TO GEN
EMPLOYEE_EMAIL = "" #WHICH TEAM MEMBER TO USE
CARD_PREFIX = "CARD_" #USED TO LABEL GENERATED CARDS

SMS_VERIFICATION = True #USE True if you want to confirm sms code and store card information in "cards.csv"



##########################


BASE_URL = "https://business.revolut.com/api/"
CURRENT_USER = BASE_URL + "user/current"
