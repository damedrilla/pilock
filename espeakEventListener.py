import requests
import time
alertUnauthorized = False
wcUser = False
alertGuestMode = False
welcomeName = ""

def speak():
    global alertUnauthorized 
    global wcUser 
    global alertGuestMode 
    global welcomeName 
    while True:
        if alertUnauthorized:
            try:
                requests.get('http://127.0.0.1:5001/deny')
            except:
                pass 
            alertUnauthorized = False
        if wcUser:
            speech = "welcome! " + welcomeName
            try:
                requests.get('http://127.0.0.1:5001/welcomeUser/' + welcomeName)
            except:
                pass
            wcUser = False
        if alertGuestMode:
            speech = "the door is open, no need to tap"
            try:
                requests.get('http://127.0.0.1:5001/guestModeIsOn')
            except:
                pass
            alertGuestMode = False
        else:
            time.sleep(0.5)

def sayUnauthorized():
    global alertUnauthorized 
    alertUnauthorized = True
    
    
def welcomeUser(name):
    global wcUser
    global welcomeName
    wcUser = True
    welcomeName = name
    
def sayGuestMode():
    global alertGuestMode
    alertGuestMode = True