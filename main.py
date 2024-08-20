import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import requests
import schedule as __schedule
import json
from datetime import datetime
import socket
from threading import Thread
from getCurrentSchedule import currentSchedule
from rest_endpoint import endpoint
from lock_state import changeLockState
import urllib.request
import time
import os

currSched = []
isFacultyPresent = False
localMode = False


def isFacultysTimeNow(name):
    global isFacultyPresent
    sc = currentSchedule(localMode)
    try:
        if sc["schedule"][0]["instructor"] == name:
            print(
                "Faculty detected. Students can now scan their ID until "
                + str(sc["schedule"][0]["time_end"])
            )
            isFacultyPresent = True
            changeLockState("unlock")
            __schedule.every().day.at(
                str(sc["schedule"][0]["time_end"]), "Asia/Manila"
            ).do(change_inst_state)
    except Exception:
        print("nah not your time yet fam")
    return


def isStudAllowedtoEnter(section):
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
        if curr_sched[0]["section"] == section:
            sectionFound = True
        else:
            sectionFound = False
    except Exception:
        sectionFound = False

    if sectionFound:
        changeLockState("unlock")
        print("get in homie")
    else:
        changeLockState("lock")
        print("no blyat")


def checkUser(id):
    global localMode
    uid = str(id).replace("(", "")
    sectionExists = False
    parseUser = []
    try:
        try:
            userRes = requests.get("http://152.42.167.108/api/students/" + uid)
            parseUser = json.loads(userRes.text)
        except Exception:
            students_bak = open("students.json")
            parseStuds = json.load(students_bak)
            for studs in range(len(parseStuds["students"])):
                if uid == parseStuds["students"][studs]["tag_uid"]:
                    parseUser.append(parseStuds["students"][studs])
                    break
    except Exception as e:
        print(str(e))

    try:
        section = parseUser[0]["section"]
    except Exception:
        try:
            instructor_list = requests.get("http://152.42.167.108/api/instructors")
            inst = json.loads(instructor_list.text)
            print(len(inst["instructors"]))
            for instr in range(len(inst["instructors"])):
                print(inst["instructors"][instr]["tag_uid"])
                if str(id) == inst["instructors"][instr]["tag_uid"]:
                    isFacultysTimeNow(inst["instructors"][instr]["instructor_name"])
        except Exception:
            print("nah")
    else:
        sectionExists = True

    if sectionExists:
        isStudAllowedtoEnter(section)
    else:
        print("This student doesn't exist. Are you real?")


# For every :00 minute of hour, fetch the latest data from the cloud for backup.
def backup():
    global localMode
    if localMode == False:
        schedres = requests.get("http://152.42.167.108/api/schedules")
        with open("schedules.json", "w") as f:
            json.dump(schedres.json(), f)

        facultyres = requests.get("http://152.42.167.108/api/instructors")
        with open("faculty.json", "w") as f:
            json.dump(facultyres.json(), f)

        studentres = requests.get("http://152.42.167.108/api/students")
        with open("students.json", "w") as f:
            json.dump(studentres.json(), f)
    else:
        return


def isInternetUp():
    global localMode
    try:
        host = socket.gethostbyname("1.1.1.1")
        s = socket.create_connection((host, 80), 2)
        s.close()
        cloud_status = urllib.request.urlopen("http://152.42.167.108/").getcode()
        if cloud_status == 200:
            print("Connected to server")
            localMode = False
    except Exception:
        print(
            "No Internet connection or the server is unavailable. Switching to local mode. "
        )
        localMode = True


# For every second, check if the internet connection and the cloud server is up.
def internetCheck():
    while True:
        isInternetUp()
        time.sleep(1)


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
    print("No faculty mode enabled.")
    isFacultyPresent = False
    return __schedule.CancelJob


def main():
    __schedule.every().hour.at(":00").do(backup)
    while True:

        reader = SimpleMFRC522()
        try:
            cardID = input("Scan your card: ")
            print("Scan your ID card:")
            cardData = reader.read_id()
            cardUID = cardData.split(',')
            print("ID: " + str(cardUID[0]))
            checkUser(cardUID[0])
            checkUser(cardID)
        except Exception:
            GPIO.cleanup()
            continue


try:
    os.system("cls")
except:
    os.system("clear")

t1 = Thread(target=internetCheck)
t2 = Thread(target=main)
t4 = Thread(target=runscheduled)
t5 = Thread(target=endpoint)

t1.start()
t2.start()
t4.start()
t5.start()
