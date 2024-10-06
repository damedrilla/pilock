from datetime import datetime
import time
from threading import Thread
from getCurrentSchedule import currentSchedule
from internetCheck import localMode
from facPrescenceController import getFacultyPrescenceState
import json

isUnauthorizedWarningUp = False
isNoFacWarningUp = False
shouldGreet = False
reg_user_tryna_enter = False
returnToDefaultMsg = True
doesUserExit = False
isOverGracePeriod = False
section = " "
person_to_greet = ""
remote_unlock = False
isLCDconnected = False
justSayWelcome = False
noNFC = False

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
    global remote_unlock
    global isOverGracePeriod
    global justSayWelcome
    global noNFC
    
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
                and not remote_unlock
                and not isOverGracePeriod
                and not justSayWelcome
                and not noNFC
            ):
                try:
                    sched_data = currentSchedule()
                except Exception:
                    continue
                current_subject = ""
                block = ""
                try:
                    current_subject = sched_data["course_title"]
                    block = sched_data["section"]
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
                    inst_status = ""
                    try:
                        inst_presc = getFacultyPrescenceState()
                        if current_subject == "Vacant" or current_subject == "Guest Mode":
                            inst_status = ""
                        elif inst_presc == 1:
                            inst_status = "Faculty is present"
                        else:
                            inst_status = 'Faculty is absent'
                    except Exception as e:
                        if current_subject == "Vacant" or current_subject == "Guest Mode":
                            inst_status = ""
                    lcd.clear()
                    lcd.write_string(current_time)
                    lcd.cursor_pos = (1, 0)
                    lcd.write_string(current_subject)
                    lcd.cursor_pos = (2, 0)
                    lcd.write_string(block)
                
                    timeChanged = False
                time.sleep(0.5)
            elif isUnauthorizedWarningUp:
                returnToDefaultMsg = False
                lcd.clear()
                lcd.cursor_pos = (0, 0)
                lcd.write_string("Access denied!")
                time.sleep(1.5)
                isUnauthorizedWarningUp = False
                returnToDefaultMsg = True
            elif isNoFacWarningUp:
                returnToDefaultMsg = False
                lcd.clear()
                lcd.write_string("No faculty is present!")
                lcd.cursor_pos = (1, 0)
                lcd.write_string("Access denied!")
                time.sleep(1.5)
                isNoFacWarningUp = False
                returnToDefaultMsg = True
            elif shouldGreet:
                returnToDefaultMsg = False
                lcd.clear()
                lcd.write_string("Welcome! " + person_to_greet)
                time.sleep(1.5)
                shouldGreet = False
                returnToDefaultMsg = True
            elif doesUserExit:
                returnToDefaultMsg = False
                lcd.clear()
                lcd.write_string("Thank you, come again!")
                time.sleep(1.5)
                doesUserExit = False
                returnToDefaultMsg = True
            elif reg_user_tryna_enter:
                returnToDefaultMsg = False
                lcd.clear()
                lcd.write_string("Sorry, ")
                lcd.cursor_pos = (1,0)
                lcd.write_string("Not your time yet!")
                time.sleep(1.5)
                reg_user_tryna_enter = False
                returnToDefaultMsg = True
            elif remote_unlock:
                returnToDefaultMsg = False
                lcd.clear()
                lcd.write_string("Remotely unlocked")
                lcd.cursor_pos = (1,0)
                lcd.write_string("Welcome!")
                time.sleep(1.5)
                remote_unlock = False
                returnToDefaultMsg = True
            elif isOverGracePeriod:
                returnToDefaultMsg = False
                lcd.clear()
                lcd.write_string("15 mins grace period")
                lcd.cursor_pos = (1,0)
                lcd.write_string("has passed.")
                lcd.cursor_pos = (2,0)
                lcd.write_string("Access denied!")
                time.sleep(1.5)
                isOverGracePeriod = False
                returnToDefaultMsg = True
            elif justSayWelcome:
                returnToDefaultMsg = False
                lcd.clear()
                lcd.write_string("Welcome, faculty!")
                time.sleep(1.5)
                justSayWelcome = False
                returnToDefaultMsg = True
            elif noNFC:
                returnToDefaultMsg = False
                lcd.clear()
                lcd.write_string("Please connect the")
                lcd.cursor_pos = (1,0)
                lcd.write_string("NFC reader!")
                time.sleep(1.5)
                noNFC = False
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

def remotelyUnlocked():
    global remote_unlock
    remote_unlock = True

def showLate():
    global isOverGracePeriod
    isOverGracePeriod = True

def welcome():
    global justSayWelcome
    justSayWelcome = True
    
def noReader():
    global noNFC
    noNFC = True