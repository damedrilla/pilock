import os
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
            speech = "access denied!"
            os.system('/usr/bin/espeak "{}"'.format(speech))
            alertUnauthorized = False
        elif wcUser:
            speech = "welcome! " + welcomeName
            os.system('/usr/bin/espeak "{}"'.format(speech))
            wcUser = False
        elif alertGuestMode:
            speech = "the door is open, no need to tap"
            os.system('/usr/bin/espeak "{}"'.format(speech))
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