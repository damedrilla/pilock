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
)
from internetCheck import internetCheck, localMode

logger = logging.getLogger(__name__)
coloredlogs.install(level="DEBUG", logger=logger)

currSched = []
isFacultyPresent = True
isFacultyPresentAlreadySet = False
localMode = False
internetWarningDone = False
BASE_API_URL = "https://www.pilocksystem.live/api/"
guestMode = False


def getCurrSched():
    global currSched
    global localMode
    global guestMode
    currSched = currentSchedule(localMode)
    try:
        if currSched["sched_type"] == "Event":
            guestMode = True
        else:
            guestMode = False
    except Exception:
        guestMode = False


def isFacultysTimeNow(name, uid):
    global isFacultyPresent
    global isFacultyPresentAlreadySet

    # Handling JSON on python Aware emojicon
    # Depends on the current localMode value, the currentSchedule method gives different types of data
    # It's either a string or a dictionary (or hash map whatever you wanna call it lole)
    # These try-catch (abominations) blocks below handles the JSON data that
    # the method gives to make it sure that the value we pass is always a JSON encoded data.
    sc = currentSchedule(localMode)
    sc_parsed = []
    try:
        try:
            # No schedule found
            sc_parsed = sc["status"]
        except KeyError:
            # Schedule from web API
            sc_parsed = sc["schedule"][0]
    except Exception:
        # Offline backup
        sc_parsed = sc

    try:
        if sc_parsed["instructor"] == name:
            isFacultyPresent = True
            changeLockState("unlock")
            requests.post("http://152.42.167.108/api/attend/" + str(uid))
            if not isFacultyPresentAlreadySet:
                logger.info(
                    "Faculty detected. Students can now scan their ID until "
                    + str(sc["schedule"][0]["time_end"])
                )
                isFacultyPresentAlreadySet = True
                __schedule.every().day.at(str(sc["schedule"][0]["time_end"])).do(
                    change_inst_state
                )
            elif isFacultyPresentAlreadySet:
                logger.info("Faculty already present. No scheduling needed.")
    except Exception:
        logger.warning("nah not your time yet fam")
    return


def isStudAllowedtoEnter(section, uid):
    global isFacultyPresent
    sectionFound = False

    # bouta run out of names yo
    curr_sched = currentSchedule(localMode)
    print(curr_sched)
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    current_weekday = now.strftime("%A")
    print("\nCurrent time and day is: " + current_time + " " + current_weekday)

    if not isFacultyPresent:
        changeLockState("lock")
        return print("Instructor not here yet!")

    try:
        if curr_sched["schedule"][0]["section"] == section:
            sectionFound = True
        else:
            sectionFound = False
    except Exception:
        sectionFound = False

    if sectionFound:
        res = requests.post("http://152.42.167.108/api/attend/" + str(uid))
        print(res.text)
        changeLockState("unlock")
        print("get in homie")
    else:
        changeLockState("lock")
        print("no blyat")


def checkUser(id):
    global localMode
    uid = int(id, 16)
    parseUser = []
    isStudent = False
    isInstructor = False

    try:
        parseUser = getStudent(localMode, uid)
        parseUser["section"]
        isStudent = True
    except Exception:
        try:
            parseUser = getFaculty(localMode, uid)
            parseUser["instructor_name"]
            isInstructor = True
        except Exception:
            showUnauthorized()

    if isStudent:
        isStudAllowedtoEnter(parseUser["section"], uid)
    elif isInstructor:
        isFacultysTimeNow(parseUser["instructor_name"], parseUser["tag_uid"])


# For every :00 minute of hour, fetch the latest data from the cloud for backup.
def backup():
    global localMode
    if localMode == False:
        try:
            schedres = requests.get(BASE_API_URL + "schedules")
            with open("schedules.json", "w") as f:
                json.dump(schedres.json(), f)
            logger.info("Fetched latest data from schedules for backup.")
        except Exception:
            logger.critical("Blank response. Schedules data might be empty!")

        try:
            facultyres = requests.get(BASE_API_URL + "instructors")
            with open("faculty.json", "w") as f:
                json.dump(facultyres.json(), f)
            logger.info("Fetched latest data from instructors for backup.")
        except Exception:
            logger.critical("Blank response. Faculty data might be empty!")

        try:
            studentres = requests.get(BASE_API_URL + "students")
            with open("students.json", "w") as f:
                json.dump(studentres.json(), f)
            logger.info("Fetched latest data from students for backup.")
        except Exception:
            logger.critical("Blank response. Students data might be empty!")

        try:
            eventres = requests.get(BASE_API_URL + "events")
            with open("events.json", "w") as f:
                json.dump(eventres.json(), f)
            logger.info("Fetched latest data from events for backup.")
        except Exception:
            logger.critical("Blank response. Events data might be empty!")

        try:
            eventres = requests.get(BASE_API_URL + "makeupscheds")
            with open("makeupclass.json", "w") as f:
                json.dump(eventres.json(), f)
            logger.info("Fetched latest data from make-up schedules for backup.")
        except Exception:
            logger.critical(
                "Blank response. Make-up class schedules data might be empty!"
            )
    else:
        return


# For every second, check if the internet connection and the cloud server is up.


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
    while True:
        reader = SimpleMFRC522()
        try:
            print("Scan your ID card:")
            cardData = reader.read_id()
            cardDataInHex = f"{cardData:x}"
            minusMfgID = cardDataInHex[:-2]
            big_endian = bytearray.fromhex(str(minusMfgID))
            big_endian.reverse()
            little_endian = "".join(f"{n:02X}" for n in big_endian)
            print(
                "ID: "
                + str(cardData)
                + " Little Endian ID: "
                + str(int(little_endian, 16))
            )
            checkUser(int(little_endian, 16))
        except KeyboardInterrupt:
            GPIO.cleanup()
            continue
        # uid = input("Input ID")
        # cardDataInHex = f"{int(uid):x}"
        # minusMfgID = cardDataInHex[:-2]
        # big_endian = bytearray.fromhex(str(minusMfgID))
        # big_endian.reverse()
        # little_endian = "".join(f"{n:02X}" for n in big_endian)
        # checkUser(little_endian)


t1 = Thread(target=internetCheck)
t2 = Thread(target=main)
t3 = Thread(target=lcdScreenController)
t4 = Thread(target=runscheduled)
t5 = Thread(target=endpoint)

t1.start()
t2.start()
# t3.start()
t4.start()
t5.start()
