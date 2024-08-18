from getCurrentSchedule import currentSchedule
from internetCheck import isInternetUp, localMode
from timecheck import timeCheck
from datetime import datetime
from internetCheck import isInternetUp
import requests
import json
import time


def getFacUID(name):
    localMode = isInternetUp()
    if not localMode:
        try:
            instructor_list = requests.get(
                "https://www.pilocksystem.live/api/instructors", timeout=2
            )
            inst = json.loads(instructor_list.text)
            for instr in range(len(inst["instructors"])):
                try:
                    inst_name = inst["instructors"][instr]["instructor_name"]
                    # print(uid_no_lead)
                    if str(name) == str(inst_name):
                        return inst["instructors"][instr]["tag_uid"]
                except Exception:
                    continue
        except Exception as e:
            return 0
    else:
        try:
            faculty_bak = open("backup_data/faculty.json")
            inst = json.load(faculty_bak)
            for instr in range(len(inst["instructors"])):
                try:
                    inst_name = inst["instructors"][instr]["instructor_name"]
                    # print(uid_no_lead)
                    if str(name) == str(inst_name):
                        return inst["instructors"][instr]["tag_uid"]
                except Exception:
                    continue
        except Exception as e:
            return 0


def tracker():
    while True:
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        try:
            state = open("backup_data/instructor_prescence.json")
            parsed_state = json.load(state)
            _end = parsed_state["time_end"]
            curr_sched = currentSchedule()
            if curr_sched["code"] == 200:
                curr_sched_end = curr_sched["time_end"]
                faculty_uid = getFacUID(str(curr_sched["instructor"]))
                isCurrentScheduleOver = timeCheck(
                    "", "", "", time_end=_end, currTime=current_time
                )
            else:
                curr_sched_end = ""
                isCurrentScheduleOver = True
                faculty_uid = 0

            if isCurrentScheduleOver:
                data = {
                    "time_end": curr_sched_end,
                    "isInstructorPresent": 0,
                    "uid": faculty_uid,
                }
                with open("backup_data/instructor_prescence.json", "w") as f:
                    json.dump(data, f)
                    f.close()
            time.sleep(1)
            state.close()
        except Exception as e:
            print(e)
            time.sleep(1)