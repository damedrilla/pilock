import requests
import json
from timecheck import timeCheck
from datetime import datetime
import coloredlogs, logging
from internetCheck import isInternetUp

logger = logging.getLogger(__name__)
coloredlogs.install(level="DEBUG", logger=logger)


# The goal of this method is to make sure that regardless of
# connection status, the one we see in the Web API will have the
# same key-value output as the one in the backup files for smooth transition
# from online to local mode. Scroll to bottom for more details.
def currentSchedule():
    localMode = isInternetUp()
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    current_weekday = now.strftime("%A")

    if localMode == False:
        try:
            currentSchedule = requests.get(
            "https://www.pilocksystem.live/api/schedules/current", timeout=2
            )
            sched = json.loads(currentSchedule.text)
            parsed_schedule = []
            parsed_schedule = sched["schedule"][0]
        except Exception:
            try:
                parsed_schedule = sched["event"][0]
            except:
                parsed_schedule = sched
        # schedStrip = str(sched['schedule']).strip('[]')
        return parsed_schedule
    else:
        try:
            schedule_bak = open("backup_data/schedules.json")
            events_bak = open("backup_data/events.json")
            make_up_bak = open("backup_data/makeupclass.json")

            parseSched = json.load(schedule_bak)
            parseEvents = json.load(events_bak)
            parseMakeup = json.load(make_up_bak)

            # We can close them, since they are in the buffer anyway.
            schedule_bak.close()
            events_bak.close()
            make_up_bak.close()
            
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


# Line 28-30 demonstrated how it works. In local mode, the only data we pass is
# the entire value of an index, that means they don't have a parent key. The Web API
# is the opposite of it, as it gives us the entire thing.

# Web API data example
# {
#     "event": [
#         {
#             "id": 1,
#             "sched_type": "Event",
#             "title": "lmfao",
#             "description": "asdasdsadnaskdmasdasd",
#             "date": "2024-07-28",
#             "event_start": "14:05:00",
#             "event_end": "14:51:00",
#         }
#     ]
# }

# Example data on local mode (much cleaner)
# {
#     "id": 1,
#     "sched_type": "Event",
#     "title": "lmfao",
#     "description": "asdasdsadnaskdmasdasd",
#     "date": "2024-07-28",
#     "event_start": "14:05:00",
#     "event_end": "14:51:00",
# }

# So instead of having a pain of traversing through the child keys when fetching online, 
# this method will ensure that the data we get online will follow the schema
# of the one when we fetch on backup data. Less error prone and easy to debug. 