import requests
import json
from timecheck import isThisTheTime
from datetime import datetime
def currentSchedule(conn_status):
    localMode = conn_status
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    current_weekday = now.strftime('%A')

    if localMode == False:
        currentSchedule = requests.get('http://152.42.167.108/api/schedules/current')
        sched = currentSchedule.json()
        # schedStrip = str(sched['schedule']).strip('[]')
        return json.loads(currentSchedule.text)
    else:
        schedule_bak = open('schedules.json')
        parseSched = json.load(schedule_bak)
        for sch in range(len(parseSched['schedules'])):
            timeStart = parseSched['schedules'][sch]['time_start']
            timeEnd = parseSched['schedules'][sch]['time_end']
            isCorrectSchedule = isThisTheTime(timeStart, timeEnd, current_time)
            if isCorrectSchedule == True and current_weekday == parseSched['schedules'][sch]['days']:
                right_schedule = parseSched['schedules'][sch]
                return json.dumps(right_schedule)
            else:
                continue
        else:
            return json.dumps({'status': 404})
        