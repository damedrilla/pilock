import RPi.GPIO as GPIO
from py122u import nfc
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
    showLate,
    welcome,
    noReader
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
from facPrescenceController import changeFacultyPrescenceState, getFacultyPrescenceState, getAllPrescenceData, resetState
from essential_data_sync import esse_sync
import sqlite3
import datetime

logger = logging.getLogger(__name__)
logging.basicConfig(filename="pilock.log", encoding="utf-8", level=logging.INFO)
coloredlogs.install(level="DEBUG", logger=logger)

BASE_API_URL = "https://www.pilocksystem.live/api/"
readerConnected = False
reader = ""

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
            greetUser(name)
            welcomeUser(name)
            changeLockState("unlock")
            # os.system('/usr/bin/espeak "{}"'.format(speech))
            try:
                req = requests.post(
                    BASE_API_URL + "attendinst/" + str(uid).zfill(10), timeout=5
                )
            except Exception:
                pass
            if getFacultyPrescenceState() == 0:
                logger.info(
                    "Faculty detected. Students can now scan their ID until "
                    + str(sc["time_end"])
                )
                changeFacultyPrescenceState(uid)
            else:
                logger.info("Faculty already present. No scheduling needed.")
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
    start_time = time.time()
    uid = str(id).zfill(10)
    parseUser = []
    isStudent = False
    isInstructor = False
    registered = False
    curr_inst_uid = getAllPrescenceData()['uid']
    isInstructorPresent = getFacultyPrescenceState()
    guestMode = guestMode_QuestionMark()
    chime()
    if guestMode:
        sayGuestMode()
        time.sleep(0.5)
        logger.debug("Guest mode is enabled!")
        return

    # if uid == "0274065971":
    #     resetState()
    #     changeLockState("unlock")
    #     logger.debug("Master key detected!")
    #     return

    try:
        # Return codes
        # 200 -> Allowed to enter
        # 401 -> Faculty is absent
        # 403 -> Not enrolled
        # 404 | 500 -> Not registered
        try:
            parseUser = getStudentData(id)
            section = parseUser["program"]
            registered = True
        except:
            raise Exception(logger.warning("Skipping student check"))
        can_they_enter = getStudent(uid)
        print(can_they_enter)
        if can_they_enter == 200:
            changeLockState("unlock")
            welcomeUser(parseUser["first_name"])
            greetUser(parseUser["first_name"])
        elif can_they_enter == 401:
            changeLockState("lock")
            showNoFacultyYet(section)
            sayAbsent()
        elif can_they_enter == 399:
            changeLockState('lock')
            showLate()
            sayUnauthorized()
        elif can_they_enter == 403:
            changeLockState("lock")
            showRegisteredButOutsideOfSchedule()
            sayUnauthorized()
        elif can_they_enter == 404 and registered:
            changeLockState("lock")
            showRegisteredButOutsideOfSchedule()
            sayUnauthorized()
            
        isStudent = True
        logger.debug("ID holder is a student!")
    except Exception as e:
        print(e)
        try:
            if isInstructorPresent == 1:
                if curr_inst_uid == uid:
                  changeLockState("unlock")
                  welcome()
                  return
                else:
                    raise Exception(logger.warning("Faculty already present, skipping faculty check"))
            else:
                parseUser = getFaculty(uid)
                name = parseUser["instructor_fname"] + " " +parseUser['instructor_lname']
                isInstructor = True
                logger.debug("ID holder is a faculty!")
        except Exception as e:
            changeLockState("lock")
            sayUnauthorized()
            logger.warning("ID holder is not registered!")
            showUnauthorized()

    if isInstructor:
        isFacultysTimeNow(name, uid)
        print("--- %s seconds ---" % (time.time() - start_time))
    else:
        print("--- %s seconds ---" % (time.time() - start_time))
        return


# Run any pending scheduled task, if there's any.
def runscheduled():
    # Run all scheduled task at bootup. (Note: Comment out on production.)
    __schedule.run_all()
    while True:
        __schedule.run_pending()
        time.sleep(1)

def checkReader():
    global reader
    global readerConnected
    while True:
        try:
            reader = nfc.Reader()
            readerConnected = True
            time.sleep(1)
        except Exception as e:
            noReader()
            logger.warning("Please attach the NFC reader!")
            readerConnected = False
            time.sleep(1)
            
def main():
    # Clear log file on start
    #__schedule.every().hour.at(":00").do(backup)
    # __schedule.every(5).minutes.do(backup)
    global readerConnected
    __schedule.every(5).seconds.do(esse_sync)
    try:
        open('pilock.log', 'w').close()
    except:
        logger.warning("Error clearing log file!")
    
    while True:
        try:
            while True:
                cardPresent = False
                uid = ""
                uid_parsed = "0x"
                if not readerConnected:
                    time.sleep(1)
                else:
                    try:
                        reader.connect()
                        reader.mute_buzzer()
                        uid = reader.get_uid()
                        uid = uid[::-1]
                        for _byte in range(len(uid)):
                            uid_parsed += "".join(f'{uid[_byte]:x}')
                        cardPresent = True
                    except Exception as e:
                        pass
                    if cardPresent:
                        logger.info(
                            "Card detected! UID: "
                            + str(int(uid_parsed, 0))
                        )
                        checkUser(int(uid_parsed, 0))
                    else:
                        pass
        except KeyboardInterrupt:
            GPIO.cleanup()
        except:
            time.sleep(1)

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
nfc_checker = Thread(target=checkReader)

main_thread.start()
lcd_thread.start()
task_scheduler_thread.start()
inst_prescence_tracker_thread.start()
exit_listener_thread.start()
openvpn_thread.start()
tts_thread.start()
rest_endpoint_thread.start()
nfc_checker.start()