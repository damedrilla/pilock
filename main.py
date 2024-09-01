import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import requests
import schedule as __schedule
import json
from threading import Thread
import time
import coloredlogs, logging
from getCurrentSchedule import currentSchedule
from rest_endpoint import endpoint
from lock_state import changeLockState
from getFaculty import getFaculty
from getStudent import getStudent
from LCDcontroller import (
    lcdScreenController,
    showUnauthorized,
    showNoFacultyYet,
    greetUser,
    showRegisteredButOutsideOfSchedule,
    showLate
)
from backup import backup
from getStudentData import getStudentData
from espeakEventListener import (
    sayUnauthorized,
    sayGuestMode,
    speak,
    welcomeUser,
    chime,
    sayAbsent,
)
from guestModeTracker import guestMode_QuestionMark
from facIsPresentTracker import tracker
from exitEventListener import exitListener
from openvpn import connectionSwitcher
from facPrescenceController import changeFacultyPrescenceState, getFacultyPrescenceState, getAllPrescenceData
import sqlite3
import datetime

logger = logging.getLogger(__name__)
logging.basicConfig(filename="pilock.log", encoding="utf-8", level=logging.INFO)
coloredlogs.install(level="DEBUG", logger=logger)

BASE_API_URL = "https://www.pilocksystem.live/api/"


# Reminder: Calling change lock state methods should always be the first
# operation if the user satisfies the authentication algorithms
# even if the POST request for attendance fails.
# You don't want them waiting for a while just for the door to open.


def isFacultysTimeNow(name, uid):
    # Handling JSON on python Aware emojicon
    # Depends on the current localMode value, the currentSchedule method gives different types of data
    # It's either a string or a dictionary (or hash map whatever you wanna call it lole)
    # These try-catch (abominations) blocks below handles the JSON data that
    # the method gives to make it sure that the value we pass is always a JSON encoded data.
    sc = currentSchedule()
    sc_parsed = []
    try:
        # No schedule found
        sc_parsed = sc["status"]
    except KeyError:
        # Schedule from web API or backup
        sc_parsed = sc

    try:
        if sc_parsed["instructor"] == name:
            changeLockState("unlock")
            greetUser(name)
            welcomeUser(name)
            # os.system('/usr/bin/espeak "{}"'.format(speech))
            try:
                req = requests.post(
                    BASE_API_URL + "attendinst/" + str(uid).zfill(10), timeout=5
                )
                logger.info(print(json.loads(req.text)))
            except Exception:
                pass
            if getFacultyPrescenceState() == 0:
                logger.info(
                    "Faculty detected. Students can now scan their ID until "
                    + str(sc["time_end"])
                )
                changeFacultyPrescenceState()
            else:
                logger.info("Faculty already present. No scheduling needed.")
                welcomeUser(name)
                # os.system('/usr/bin/espeak "{}"'.format(speech))
        else:
            changeLockState("lock")
            showRegisteredButOutsideOfSchedule()
            logger.warning(
                "Faculty " + name + " tried to enter outside of their schedule!"
            )
            sayUnauthorized()
            # os.system('/usr/bin/espeak "{}"'.format(speech))
    except Exception:
        changeLockState("lock")
        showRegisteredButOutsideOfSchedule()
        sayUnauthorized()
        logger.warning("Faculty " + name + " tried to enter outside of their schedule!")
    return

def checkUser(id):
    # Make sure leading zeroes are gone
    uid = int(id)
    parseUser = []
    isStudent = False
    isInstructor = False
    registered = False
    guestMode = guestMode_QuestionMark()
    if guestMode:
        sayGuestMode()
        time.sleep(0.5)
        return

    if uid == 274065971:
        changeLockState("unlock")
        logger.debug("Master key detected!")
        return

    try:
        # Return codes
        # 200 -> Allowed to enter
        # 401 -> Faculty is absent
        # 403 -> Not enrolled
        # 404 | 500 -> Not registered
        try:
            parseUser = getStudentData(uid)
            section = parseUser["section"]
            registered = True
        except:
            raise Exception("unregistered")
        can_they_enter = getStudent(uid)
        print(can_they_enter)
        if can_they_enter == 200:
            changeLockState("unlock")
            welcomeUser(parseUser["name"])
            greetUser(parseUser["name"])
        elif can_they_enter == 401:
            changeLockState("lock")
            showNoFacultyYet(section)
            sayAbsent()
        elif can_they_enter == 399:
            changeLockState('lock')
            showLate()
            sayUnauthorized()
        elif registered:
            changeLockState("lock")
            showRegisteredButOutsideOfSchedule()
            sayUnauthorized()
        else:
            changeLockState("lock")
            raise Exception("nah dude")
        isStudent = True
        logger.debug("ID holder is a student!")
    except Exception as e:
        print(e)
        try:
            parseUser = getFaculty(uid)
            parseUser["instructor_name"]
            isInstructor = True
            logger.debug("ID holder is a faculty!")
        except Exception as e:
            changeLockState("lock")
            sayUnauthorized()
            logger.warning("ID holder is not registered!")
            showUnauthorized()

    if isStudent:
        # isStudAllowedtoEnter(parseUser["section"], uid, parseUser["name"])
        return
    elif isInstructor:
        isFacultysTimeNow(parseUser["instructor_name"], uid)


# Run any pending scheduled task, if there's any.
def runscheduled():
    # Run all scheduled task at bootup. (Note: Comment out on production.)
    __schedule.run_all()
    while True:
        __schedule.run_pending()
        time.sleep(1)


def main():
    # Clear log file on start
    try:
        open("pilock.log", "w").close()
    except:
        logger.warning("Failed to clear log files!")

    __schedule.every().hour.at(":00").do(backup)
    reader = SimpleMFRC522()
    while True:
        try:
            logger.info("Waiting for an ID...")
            cardData = reader.read_id()
            cardDataInHex = f"{cardData:x}"
            minusMfgID = cardDataInHex[:-2]
            big_endian = bytearray.fromhex(str(minusMfgID))
            big_endian.reverse()
            little_endian = "".join(f"{n:02X}" for n in big_endian)
            logger.info(
                "User ID "
                + str(cardData)
                + " scanned and converted to little endian ID of: "
                + str(int(little_endian, 16))
            )
            chime()
            checkUser(int(little_endian, 16))
        except KeyboardInterrupt:
            GPIO.cleanup()
        except:
            GPIO.cleanup()

        # Uncomment below and comment the try-catch block above
        # if testing in windows PC

        # uid = input("Input ID")
        # cardDataInHex = f"{int(uid):x}"
        # minusMfgID = cardDataInHex[:-2]
        # big_endian = bytearray.fromhex(str(minusMfgID))
        # big_endian.reverse()
        # little_endian = "".join(f"{n:02X}" for n in big_endian)
        # checkUser(uid)


# Threads
main_thread = Thread(target=main)
tts_thread = Thread(target=speak)
lcd_thread = Thread(target=lcdScreenController)
task_scheduler_thread = Thread(target=runscheduled)
rest_endpoint_thread = Thread(target=endpoint)
inst_prescence_tracker_thread = Thread(target=tracker)
exit_listener_thread = Thread(target=exitListener)
openvpn_thread = Thread(target=connectionSwitcher)

main_thread.start()
lcd_thread.start()
task_scheduler_thread.start()
inst_prescence_tracker_thread.start()
exit_listener_thread.start()
openvpn_thread.start()
tts_thread.start()
rest_endpoint_thread.start()
