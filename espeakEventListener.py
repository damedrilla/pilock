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
            os.seteuid(1000)
            speech = "access denied!"
            os.system('espeak -v en "access denied" --stdout | aplay')
            alertUnauthorized = False
        if wcUser:
            speech = "welcome! " + welcomeName
            os.system('/usr/bin/espeak "{}" > /dev/null 2>&1'.format(speech))
            wcUser = False
        if alertGuestMode:
            speech = "the door is open, no need to tap"
            os.system('/usr/bin/espeak "{}" > /dev/null 2>&1'.format(speech))
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