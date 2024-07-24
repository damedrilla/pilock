import requests
import json
from timecheck import timeCheck
from datetime import datetime
import coloredlogs, logging
from internetCheck import isInternetUp

logger = logging.getLogger(__name__)
coloredlogs.install(level="DEBUG", logger=logger)


def currentSchedule():
    localMode = isInternetUp()
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    current_weekday = now.strftime("%A")

    if localMode == False:
        currentSchedule = requests.get(
            "https://www.pilocksystem.live/api/schedules/current"
        )
        sched = json.loads(currentSchedule.text)
        parsed_schedule = []
        try:
            parsed_schedule = sched["schedule"][0]
        except Exception:
            parsed_schedule = sched
        # schedStrip = str(sched['schedule']).strip('[]')
        return parsed_schedule
    else:
        schedule_bak = open("backup_data/schedules.json")
        events_bak = open("backup_data/events.json")
        make_up_bak = open("backup_data/makeupclass.json")
        parseSched = json.load(schedule_bak)
        parseEvents = json.load(events_bak)
        parseMakeup = json.load(make_up_bak)
        try:
            for events in range(len(parseEvents["events"])):
                timeStart = parseEvents["events"][events]["event_start"]
                timeEnd = parseEvents["events"][events]["event_end"]
                event_date = parseEvents["events"][events]["date"]
                isCorrectSchedule = timeCheck(
                    timeStart, timeEnd, current_time, date_scheduled=str(event_date)
                )
                if isCorrectSchedule == True:
                    right_schedule = parseEvents["events"][events]
                    right_schedule["sched_type"] = "Event"
                    return right_schedule
                else:
                    continue
        except Exception as e:
            pass

        try:
            for make_up_sch in range(len(parseMakeup["schedules"])):
                timeStart = parseMakeup["schedules"][make_up_sch]["time_start"]
                timeEnd = parseMakeup["schedules"][make_up_sch]["time_end"]
                isCorrectSchedule = timeCheck(timeStart, timeEnd, current_time)
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
            pass

        try:
            for reg_sch in range(len(parseSched["schedules"])):
                timeStart = parseSched["schedules"][reg_sch]["time_start"]
                timeEnd = parseSched["schedules"][reg_sch]["time_end"]
                isCorrectSchedule = timeCheck(timeStart, timeEnd, current_time)
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
            pass
        return {"status": 404}
