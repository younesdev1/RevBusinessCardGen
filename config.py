EMAIL = "" #Login Email Address
PASSWORD = "" # Login Password

REV_TOKEN =  ""  #COOKIES (Token)
DEVICE_ID = "" #x-device-id, all requests - No need to supply if email/password are filled
COPY_ONLY = False #Copy only, gen
GEN_NUMBER = 200 #HOW MANY CARDS TO GEN
EMPLOYEE_EMAIL = "" #WHICH TEAM MEMBER TO USE
CARD_PREFIX = "CARD_" #USED TO LABEL GENERATED CARDS
START_WITH_INDEX = 0 #INDEX WITH YOU WANT TO START CREATING YOUR CARD / COPYING YOUR CARDS EX. (44) {CARD_PREFIX}_44, {CARD_PREFIX}_45...
SMS_VERIFICATION = True #USE True if you want to confirm sms code and store card information in "cards.csv"



##########################


BASE_URL = "https://business.revolut.com/api/"
CURRENT_USER = BASE_URL + "user/current"