from getCurrentSchedule import currentSchedule
from internetCheck import isInternetUp, localMode
from timecheck import timeCheck
from datetime import datetime
from internetCheck import isInternetUp
from facPrescenceController import getAllPrescenceData
import sqlite3
import requests
import json
import time
import re

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
        reg_time = re.compile(r'^([0-1]?\d|2[0-3])(?::([0-5]?\d))?(?::([0-5]?\d))?$')
        try:
            state = getAllPrescenceData()
            _end = state["time_end"]
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
                #verify if schedule has actually ended, 
                #or the internet is just being wacky lole
                isItActuallyOver = timeCheck(
                    "", "", "", time_end=state['time_end'], currTime=current_time
                )
                if not isItActuallyOver and bool(reg_time.match(curr_sched_end)):
                    time.sleep(1)
                else:
                    con = sqlite3.connect('allowed_students.db', isolation_level=None)
                    cur = con.cursor()
                    statement = "delete from authorized"
                    cur.execute(statement)
                    params = (curr_sched_end, faculty_uid, 1)
                    cur.execute("update inst_prescence set time_end = ?, isInstructorPresent = 0, uid = ?, time_in = '' where rowid = ?", params)
                    con.close()
                    time.sleep(1)
        except Exception as e:
            print(e)
            con = sqlite3.connect('allowed_students.db', isolation_level=None)
            cur = con.cursor()
            statement = "delete from authorized"
            cur.execute(statement)
            params = ("", "", 1)
            cur.execute("update inst_prescence set time_end = ?, isInstructorPresent = 0, uid = ?, time_in = '' where rowid = ?", params)
            con.close()
            time.sleep(1)