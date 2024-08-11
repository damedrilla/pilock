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
            requests.get('http://127.0.0.1:5001/deny')
            alertUnauthorized = False
        if wcUser:
            speech = "welcome! " + welcomeName
            requests.get('http://127.0.0.1:5001/welcomeUser/' + welcomeName)
            wcUser = False
        if alertGuestMode:
            speech = "the door is open, no need to tap"
            requests.get('http://127.0.0.1:5001/guestModeIsOn')
            wcUser = False
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