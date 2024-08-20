import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import requests
import schedule as __schedule
import json
from datetime import datetime
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
)
from espeakEventListener import sayUnauthorized, sayGuestMode, speak, welcomeUser
from guestModeTracker import guestMode_QuestionMark
from internetCheck import isInternetUp
from facIsPresentTracker import tracker
import os

logger = logging.getLogger(__name__)
coloredlogs.install(level="DEBUG", logger=logger)

BASE_API_URL = "https://www.pilocksystem.live/api/"

# Reminder: Calling change lock state methods should always be the first
# operation if the user satisfies the authentication algorithms
# even if the POST request for attendance fails.
# You don't want them waiting for a while just for the door to open.
def changeFacultyPrescenceState():
    try:
        data = open("backup_data/instructor_prescence.json")
        data_parsed = json.load(data)
        data_parsed["isInstructorPresent"] = 1
        data.close()
        with open("backup_data/instructor_prescence.json", "w") as f:
            json.dump(data_parsed, f)
            f.close()
    except Exception as e:
        print(e)
        logger.critical("Error updating!")


def getFacultyPrescenceState():
    try:
        data = open("backup_data/instructor_prescence.json")
        data_parsed = json.load(data)
        data.close()
        try:
            return data_parsed["isInstructorPresent"]
        except Exception:
            return 0
    except Exception:
        return 0


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
                req = requests.post(BASE_API_URL + "attendinst/" + str(uid), timeout=5)
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
        showRegisteredButOutsideOfSchedule()
        sayUnauthorized()
        logger.warning("Faculty " + name + " tried to enter outside of their schedule!")
    return


def isStudAllowedtoEnter(
    section,
    uid,
    name,
):
    global isFacultyPresent
    sectionFound = False

    # bouta run out of names yo
    curr_sched = currentSchedule()
    print(curr_sched)
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    current_weekday = now.strftime("%A")
    print("\nCurrent time and day is: " + current_time + " " + current_weekday)

    if getFacultyPrescenceState() == 0:
        changeLockState("lock")
        showNoFacultyYet(section)
        return

    try:
        if curr_sched["section"] == section:
            sectionFound = True
        else:
            sectionFound = False
    except Exception:
        sectionFound = False

    if sectionFound:
        changeLockState("unlock")
        greetUser(name)
        welcomeUser(name)
        try:
            res = requests.post(BASE_API_URL + "attendstud/" + str(uid))
            print(res.text)
        except Exception:
            pass
    else:
        changeLockState("lock")
        sayUnauthorized()
        logger.warning("Student " + name + " tried to enter outside of their schedule!")
        showRegisteredButOutsideOfSchedule()


def checkUser(id):
    # Make sure leading zeroes are gone
    uid = int(id)
    parseUser = []
    isStudent = False
    isInstructor = False
    guestMode = guestMode_QuestionMark()
    if guestMode:
        sayGuestMode()
        time.sleep(0.5)
        return

    if uid == 274065971:
        changeLockState("unlock")
        logger.debug("Master key detected!")
        time.sleep(0.5)
        return

    try:
        parseUser = getStudent(uid)
        parseUser["section"]
        isStudent = True
        logger.debug("ID holder is a student!")
    except Exception:
        try:
            parseUser = getFaculty(uid)
            parseUser["instructor_name"]
            isInstructor = True
            logger.debug("ID holder is a faculty!")
        except Exception as e:
            changeLockState("lock")
            sayUnauthorized()
            logger.debug("ID holder is not registered!")
            showUnauthorized()

    if isStudent:
        isStudAllowedtoEnter(parseUser["section"], uid, parseUser["name"])
    elif isInstructor:
        isFacultysTimeNow(parseUser["instructor_name"], uid)


# For every :00 minute of hour, fetch the latest data from the cloud for backup.
def backup():
    localMode = isInternetUp()
    if localMode == False:
        try:
            schedres = requests.get(BASE_API_URL + "schedules")
            with open("backup_data/schedules.json", "w") as f:
                json.dump(schedres.json(), f)
            logger.info("Fetched latest data from schedules for backup.")
        except Exception:
            logger.critical("Blank response. Schedules data might be empty!")

        try:
            facultyres = requests.get(BASE_API_URL + "instructors")
            with open("backup_data/faculty.json", "w") as f:
                json.dump(facultyres.json(), f)
            logger.info("Fetched latest data from instructors for backup.")
        except Exception:
            logger.critical("Blank response. Faculty data might be empty!")

        try:
            studentres = requests.get(BASE_API_URL + "students")
            with open("backup_data/students.json", "w") as f:
                json.dump(studentres.json(), f)
            logger.info("Fetched latest data from students for backup.")
        except Exception:
            logger.critical("Blank response. Students data might be empty!")

        try:
            eventres = requests.get(BASE_API_URL + "events")
            with open("backup_data/events.json", "w") as f:
                json.dump(eventres.json(), f)
            logger.info("Fetched latest data from events for backup.")
        except Exception:
            logger.critical("Blank response. Events data might be empty!")

        try:
            eventres = requests.get(BASE_API_URL + "makeupscheds")
            with open("backup_data/makeupclass.json", "w") as f:
                json.dump(eventres.json(), f)
            logger.info("Fetched latest data from make-up schedules for backup.")
        except Exception:
            logger.critical(
                "Blank response. Make-up class schedules data might be empty!"
            )
        f.close()
    else:
        return


# Run any pending scheduled task, if there's any.
def runscheduled():
    # Run all scheduled task at bootup. (Note: Comment out on prod.)
    __schedule.run_all()
    while True:
        __schedule.run_pending()
        time.sleep(1)


# Revert back to no faculty mode after a schedule has passed.
def change_inst_state():
    global isFacultyPresent
    global isFacultyPresentAlreadySet
    logger.warning("No faculty mode enabled.")
    isFacultyPresent = False
    isFacultyPresentAlreadySet = False
    return __schedule.CancelJob


def main():
    __schedule.every().hour.at(":00").do(backup)
    reader = SimpleMFRC522()
    while True:
        try:
            logger.info('Waiting for an ID...')
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
            checkUser(int(little_endian, 16))
        except Exception as e:
            print(e)
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


t1 = Thread(target=speak)
t2 = Thread(target=main)
t3 = Thread(target=lcdScreenController)
t4 = Thread(target=runscheduled)
t5 = Thread(target=endpoint)
# t6 = Thread(target=guestMode_QuestionMark)
t7 = Thread(target=tracker)

t1.start()
t2.start()
t3.start()
t4.start()
t5.start()
# t6.start()
t7.start()
# print(localMode)
