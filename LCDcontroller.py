from RPLCD.i2c import CharLCD
from datetime import datetime
import time
from threading import Thread
from getCurrentSchedule import currentSchedule
from internetCheck import localMode

isAltScreenInfoActive = False
lcd = CharLCD(i2c_expander="PCF8574", address=0x27, port=1, cols=20, rows=4, dotsize=8)


def lcdScreenController(**kwargs):
    lcd.clear()
    timeChanged = False
    current_time = datetime.now()
    while True:
        if not isAltScreenInfoActive:
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
            if timeChanged or 'revert' in kwargs:
                lcd.clear()
                lcd.write_string(current_time)
                lcd.cursor_pos = (1, 0)
                lcd.write_string(current_subject)
                lcd.cursor_pos = (2, 0)
                lcd.write_string(current_faculty)
                timeChanged = False
            time.sleep(1)
        else:
            time.sleep(1)


def showUnauthorized():
    global isAltScreenInfoActive
    isAltScreenInfoActive = True
    lcd.clear()
    lcd.write_string('WHO THE FUCK ARE YOU LMAOOOO GET OUT')
    time.sleep(5)
    isAltScreenInfoActive = False
    lcdScreenController(revert='hell yeah')


def showNoFacultyYet():
    global isAltScreenInfoActive
    isAltScreenInfoActive = True
    print("Warning")
    time.sleep(5)
    isAltScreenInfoActive = False


def greetUser(firstName):
    global isAltScreenInfoActive
    isAltScreenInfoActive = True
    print("Warning")
    time.sleep(5)
    isAltScreenInfoActive = False
