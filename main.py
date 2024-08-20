# import RPi.GPIO as GPIO
# from mfrc522 import SimpleMFRC522
import requests
import schedule as __schedule
import timecheck
import json
from datetime import datetime
import socket
from threading import Thread
from getCurrentSchedule import currentSchedule
from rest_endpoint import endpoint
from lock_state import changeLockState
import urllib.request
import time
currSched = []
isFacultyPresent = True
localMode = False
def isInternetUp():
    global localMode
    try:
        host = socket.gethostbyname('1.1.1.1')
        s = socket.create_connection((host, 80), 2)
        s.close()
        cloud_status = urllib.request.urlopen("http://152.42.167.108/").getcode()
        if cloud_status == 200:
            print('Connected to server')
            localMode = False
    except Exception:
        print('No Internet connection or the server is unavailable. Switching to local mode. ')
        localMode = True
        
# For every :00 minute of hour, fetch the latest data from the cloud for backup.
def backup():
    if localMode == False:
        schedres = requests.get('http://152.42.167.108/api/schedules')
        with open('schedules.json', 'w') as f:
            json.dump(schedres.json(),f)
            
        facultyres = requests.get('http://152.42.167.108/api/instructors')
        with open('faculty.json', 'w') as f:
            json.dump(facultyres.json(),f)
        
        studentres = requests.get('http://152.42.167.108/api/students')
        with open('students.json', 'w') as f:
            json.dump(studentres.json(),f)
    else: 
        return
        
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
    print('No faculty mode enabled.')
    isFacultyPresent = False
    return __schedule.CancelJob
        
def main(): 
    __schedule.every().hour.at(":00").do(backup)
    while True:
        schedres = requests.get('http://152.42.167.108/api/schedules')
        currentSchedule = requests.get('http://152.42.167.108/api/schedules/current')
        print(currentSchedule.json())
        # parseSched = json.loads(schedres.text)
        schedule_bak = open('schedules.json')
        parseSched = json.load(schedule_bak)
        parseCurrentSched = json.loads(currentSchedule.text)
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        current_weekday = now.strftime('%A')
        print("\nCurrent time and day is: " +  current_time + " " + current_weekday)
        
        def isFacultysTimeNow(name):
            global isFacultyPresent
            sc = json.loads(currentSchedule.text)
            if sc['schedule'][0]['instructor'] == name:
                print('Faculty detected. Students can now scan their ID until ' + str(sc['schedule'][0]['time_end']))
                isFacultyPresent = True
                changeLockState('unlock')
                __schedule.every().day.at(str(sc['schedule'][0]['time_end']), 'Asia/Manila').do(change_inst_state)
            else:
                print('nah not your time yet fam')
            return
            
        
        def isStudAllowedtoEnter(section):
            global isFacultyPresent
            sectionFound = False
            schedules = []
            
            if isFacultyPresent == False:
                return print('Instructor not here yet!')
            
            for sch in range(len(parseSched['schedules'])):
                if str(parseSched['schedules'][sch]['section']).lower() == section.lower():
                    sectionFound = True
                    if sectionFound:
                        schedules.append(parseSched['schedules'][sch])

            if sectionFound:
                hasClassesToday = False
                for REALsched in range(len(schedules)):
                    print(schedules[REALsched]['days'])
                    if str(schedules[REALsched]['days']) == str(current_weekday):
                        canIEnter = timecheck.isThisTheTime(schedules[REALsched]['time_start'], schedules[REALsched]['time_end'], current_time)
                        if canIEnter:
                            changeLockState('unlock')
                            print("get in homie")
                            hasClassesToday = True
                            break
                        else:
                            changeLockState('lock')
                            print("wait for your turn bozo")
                            hasClassesToday = True
                            break
                
                if not hasClassesToday:
                    print("you don't have classes in this room for this day retard")
                            
            print(str(schedules))
            if not sectionFound:
                print("Invalid section")
                
        def checkUser(id):
            sectionExists = False
            userRes = []
            parseUser = []
            try:
                userRes = requests.get('http://152.42.167.108/api/students/' + str(id).replace('(', ''))
                parseUser =  json.loads(userRes.text)
            except Exception:
                print('No user found, moving to faculty query')
                
            try:
                section = parseUser['students'][0]['section']
            except Exception:
                try:
                    instructor_list = requests.get('http://152.42.167.108/api/instructors')
                    inst = json.loads(instructor_list.text)
                    print(len(inst['instructors']))
                    for instr in range(len(inst['instructors'])):
                        print(inst['instructors'][instr]['tag_uid'])
                        if str(id) == inst['instructors'][instr]['tag_uid']:
                            isFacultysTimeNow(inst['instructors'][instr]['instructor_name'])
                except Exception:
                    print('nah')
            else:
                sectionExists = True
                
            if sectionExists:
                isStudAllowedtoEnter(section)
            else:
                print("This student doesn't exist. Are you real?")
                
        # reader = SimpleMFRC522()
        
        # try:
        #     cardID = input("Scan your card: ")
        #     # print("Scan your ID card:")
        #     # cardData = reader.read()
        #     # cardUID = cardData.split(',')
        #     # print("ID: " + str(cardUID[0]))
        #     # checkUser(cardUID[0])
        #     checkUser(cardID)
        # finally:
        #     # GPIO.cleanup()
        #     continue

        cardID = input("Scan your card: ")
        checkUser(cardID)

t1 = Thread(target=internetCheck)
t2 = Thread(target=main)
t4 = Thread(target=runscheduled)
t5 = Thread(target=endpoint)

t1.start()
t2.start()
t4.start()
t5.start()