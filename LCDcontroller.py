from RPLCD.i2c import CharLCD
from datetime import datetime
import time
from threading import Thread
from getCurrentSchedule import currentSchedule
from internetCheck import localMode

isUnauthorizedWarningUp = False
isNoFacWarningUp = False
shouldGreet = False
returnToDefaultMsg = True
person_to_greet = ""

lcd = CharLCD(i2c_expander="PCF8574", address=0x27, port=1, cols=20, rows=4, dotsize=8)


def lcdScreenController():
    global isUnauthorizedWarningUp 
    global isNoFacWarningUp 
    global shouldGreet
    global person_to_greet
    global returnToDefaultMsg
    lcd.clear()
    timeChanged = False
    current_time = datetime.now()
    while True:
        if not isUnauthorizedWarningUp and not isNoFacWarningUp and not shouldGreet:
            sched_data = currentSchedule(localMode)
            current_subject = ""
            current_faculty = ""
            try:
                current_subject = sched_data["subject"]
                current_faculty = sched_data["instructor"]
            except Exception:
                try:
                    if sched_data["sched_type"] == "Event":
                        current_subject = "Guest Mode"
                except Exception:
                    current_subject = "Vacant"

            c = datetime.now()
            if current_time != c.strftime("%b-%d %I:%M %p"):
                current_time = c.strftime("%b-%d %I:%M %p")
                timeChanged = True
            if timeChanged or returnToDefaultMsg:
                lcd.clear()
                lcd.write_string(current_time)
                lcd.cursor_pos = (1, 0)
                lcd.write_string(current_subject)
                lcd.cursor_pos = (2, 0)
                lcd.write_string(current_faculty)
                timeChanged = False
            time.sleep(1)
        elif isUnauthorizedWarningUp:
                returnToDefaultMsg = False
                lcd.clear()
                lcd.write_string("WHO THE FUCK ARE YOU LMAOOOO GET OUT")
                time.sleep(5)
                isUnauthorizedWarningUp = False
                returnToDefaultMsg = True
        elif isNoFacWarningUp:
                returnToDefaultMsg = False
                lcd.clear()
                lcd.write_string("No faculty yet!")
                time.sleep(5)
                isNoFacWarningUp = False
                returnToDefaultMsg = True
        elif shouldGreet:
                returnToDefaultMsg = False
                lcd.clear()
                lcd.write_string("Welcome! " + person_to_greet)
                time.sleep(5)
                shouldGreet = False
                returnToDefaultMsg = True
        else:
            time.sleep(1)

def showUnauthorized():
    global isUnauthorizedWarningUp
    isUnauthorizedWarningUp = True


def showNoFacultyYet():
    global isNoFacWarningUp
    isNoFacWarningUp = True


def greetUser(firstName):
    global shouldGreet
    global person_to_greet
    shouldGreet = True
    person_to_greet = firstName
