# from xdd import localMode
import requests
import json
from timecheck import isThisTheTime
from datetime import datetime
def getCurrentSchedule():
    localMode = True
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    current_weekday = now.strftime('%A')
    
    if localMode == False:
        currentSchedule = requests.get('http://152.42.167.108/api/schedules/current')
        return currentSchedule.json()
    else:
        schedule_bak = open('schedules.json')
        parseSched = json.load(schedule_bak)
        for sch in range(len(parseSched['schedules'])):
            isCorrectSchedule = isThisTheTime(parseSched['schedules'][sch]['time_start'], parseSched['schedules'][sch]['time_end'], current_time)
            if isCorrectSchedule == True and current_weekday == parseSched['schedules'][sch]['days']:
                print(parseSched['schedules'][sch])
            else:
                continue
        else:
            return {'status': 404}
getCurrentSchedule()