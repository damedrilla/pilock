import requests
import json
from timecheck import isThisTheTime
from datetime import datetime
import coloredlogs, logging

logger = logging.getLogger(__name__)
coloredlogs.install(level="DEBUG", logger=logger)


def currentSchedule(conn_status):
    localMode = conn_status
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    current_weekday = now.strftime("%A")

    if localMode == False:
        currentSchedule = requests.get(
            "https://www.pilocksystem.live/api/schedules/current"
        )
        sched = currentSchedule.json()
        # schedStrip = str(sched['schedule']).strip('[]')
        return json.loads(currentSchedule.text)
    else:
        schedule_bak = open("schedules.json")
        events_bak = open("events.json")
        make_up_bak = open("makeupclass.json")
        parseSched = json.load(schedule_bak)
        parseEvents = json.load(events_bak)
        parseMakeup = json.load(make_up_bak)
        try:
            for events in range(len(parseEvents["events"])):
                timeStart = parseEvents["events"][events]["event_start"]
                timeEnd = parseEvents["events"][events]["event_end"]
                event_date = parseEvents["events"][events]["date"]
                isCorrectSchedule = isThisTheTime(
                    timeStart, timeEnd, current_time, date_scheduled=str(event_date)
                )
                if isCorrectSchedule == True:
                    right_schedule = parseEvents["events"][events]
                    right_schedule["sched_type"] = "Event"
                    return right_schedule
                else:
                    continue
        except Exception as e:
            logger.warn("BACKUP: Nothing in events")

        try:
            for make_up_sch in range(len(parseMakeup["schedules"])):
                timeStart = parseMakeup["schedules"][make_up_sch]["time_start"]
                timeEnd = parseMakeup["schedules"][make_up_sch]["time_end"]
                isCorrectSchedule = isThisTheTime(timeStart, timeEnd, current_time)
                if (
                    isCorrectSchedule == True
                    and current_weekday == parseMakeup["schedules"][make_up_sch]["days"]
                ):
                    right_schedule = parseMakeup["schedules"][make_up_sch]
                    right_schedule["sched_type"] = "Regular Class/Make-Up Schedules"
                    return right_schedule
                else:
                    continue
        except Exception as e:
            logger.warn("BACKUP: Nothing in make-up classes")

        try:
            for reg_sch in range(len(parseSched["schedules"])):
                timeStart = parseSched["schedules"][reg_sch]["time_start"]
                timeEnd = parseSched["schedules"][reg_sch]["time_end"]
                isCorrectSchedule = isThisTheTime(timeStart, timeEnd, current_time)
                if (
                    isCorrectSchedule == True
                    and current_weekday == parseSched["schedules"][reg_sch]["days"]
                ):
                    right_schedule = parseSched["schedules"][reg_sch]
                    right_schedule["sched_type"] = "Regular Class/Make-Up Schedules"
                    return right_schedule
                else:
                    continue
        except Exception as e:
            logger.warn("BACKUP: Nothing in make-up classes")
        return {"status": 404}
