from datetime import datetime
import time
from threading import Thread
from getCurrentSchedule import currentSchedule
from internetCheck import localMode

isUnauthorizedWarningUp = False
isNoFacWarningUp = False
shouldGreet = False
reg_user_tryna_enter = False
returnToDefaultMsg = True
doesUserExit = False
section = " "
person_to_greet = ""
isLCDconnected = False


def lcdScreenController():
    global isUnauthorizedWarningUp
    global isNoFacWarningUp
    global shouldGreet
    global person_to_greet
    global returnToDefaultMsg
    global reg_user_tryna_enter
    global doesUserExit
    global section
    global isLCDconnected
    try:
        from RPLCD.i2c import CharLCD

        lcd = CharLCD(
            i2c_expander="PCF8574", address=0x27, port=1, cols=20, rows=4, dotsize=8
        )
        isLCDconnected = True
    except Exception:
        print("Cannot detect I2C LCD, is it properly connected? continuing anyway...")
    if not isLCDconnected:
        return

    lcd.clear()
    timeChanged = False
    current_time = datetime.now()

    while True:
        try:
            if (
                not isUnauthorizedWarningUp
                and not isNoFacWarningUp
                and not shouldGreet
                and not reg_user_tryna_enter
                and not doesUserExit
            ):
                try:
                    sched_data = currentSchedule()
                except Exception:
                    continue
                current_subject = ""
                current_faculty = ""
                try:
                    current_subject = sched_data["course_title"]
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
                lcd.write_string("Unregistered card")
                lcd.cursor_pos = (1, 0)
                lcd.write_string("detected.")
                lcd.cursor_pos = (2, 0)
                lcd.write_string("Access denied!")
                time.sleep(5)
                isUnauthorizedWarningUp = False
                returnToDefaultMsg = True
            elif isNoFacWarningUp:
                returnToDefaultMsg = False
                lcd.clear()
                lcd.write_string(section + "'s faculty isn't here yet!")
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
            elif doesUserExit:
                returnToDefaultMsg = False
                lcd.clear()
                lcd.write_string("Thank you, come again!")
                time.sleep(5)
                doesUserExit = False
                returnToDefaultMsg = True
            elif reg_user_tryna_enter:
                returnToDefaultMsg = False
                lcd.clear()
                lcd.write_string("You can't enter right now, it's not your time yet!")
                time.sleep(5)
                reg_user_tryna_enter = False
                returnToDefaultMsg = True
            else:
                time.sleep(1)
        except Exception:
            print("LCD problem occured, please check the connections")
            return


def showUnauthorized():
    global isUnauthorizedWarningUp
    isUnauthorizedWarningUp = True


def userExit():
    global doesUserExit
    doesUserExit = True


def showRegisteredButOutsideOfSchedule():
    global reg_user_tryna_enter
    reg_user_tryna_enter = True


def showNoFacultyYet(sec):
    global isNoFacWarningUp
    global section
    isNoFacWarningUp = True
    section = sec


def greetUser(firstName):
    global shouldGreet
    global person_to_greet
    shouldGreet = True
    person_to_greet = firstName
