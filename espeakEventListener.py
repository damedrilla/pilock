import os
import time
import pyttsx3
alertUnauthorized = False
wcUser = False
alertGuestMode = False
welcomeName = ""

def speak():
    global alertUnauthorized 
    global wcUser 
    global alertGuestMode 
    global welcomeName 
    engine = pyttsx3.init()
    while True:
        if alertUnauthorized:
            speech = "access denied!"
            engine.say("I will speak this text")
            engine.runAndWait()
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