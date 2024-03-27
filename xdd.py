import requests
import timecheck
import json
from datetime import datetime

    
while True:
    schedres = requests.get('http://152.42.167.108/api/schedules')
    currentSchedule = requests.get('http://152.42.167.108/api/schedules/current')
    parseSched = json.loads(schedres.text)
    parseCurrentSched = json.loads(currentSchedule.text)
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    current_weekday = now.strftime('%A')
    print("\nCurrent time and day is: " +  current_time + " " + current_weekday)
    
    def isStudAllowedtoEnter(section):
        sectionFound = False
        schedules = []
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
                        print("get in homie")
                        hasClassesToday = True
                        break
                    else:
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
        userRes = requests.get('http://localhost:322/users/student/' + str(id))
        parseUser =  json.loads(userRes.text)
        try:
            section = parseUser['data'][0]['section']
        except IndexError:
            sectionExists = False
        else:
            sectionExists = True
            
        if sectionExists:
             isStudAllowedtoEnter(section)
        else:
            print("This student doesn't exist. Are you real?")
             
    studID = input('ID: ') 
    checkUser(studID)
    