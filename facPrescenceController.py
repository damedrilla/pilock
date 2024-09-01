import datetime
import sqlite3
import json
import coloredlogs, logging

logger = logging.getLogger(__name__)
logging.basicConfig(filename='pilock.log', encoding='utf-8', level=logging.INFO)
coloredlogs.install(level="DEBUG", logger=logger)
def changeFacultyPrescenceState():
    try:
        con = sqlite3.connect('allowed_students.db', isolation_level=None)
        cur = con.cursor()
        param = (str(datetime.datetime.now().time().replace(microsecond=0)),)
        cur.execute("update inst_prescence set isInstructorPresent = 1, time_in = ? where rowid = 1", param)
        con.close()
    except Exception as e:
        print(e)
        logger.critical("Error updating!")


def getFacultyPrescenceState():
    try:
        con = sqlite3.connect('allowed_students.db', isolation_level=None)
        cur = con.cursor()
        cur.execute('select isInstructorPresent from inst_prescence where rowid = 1')
        row = cur.fetchone()
        try:
            return row[0]
        except Exception:
            return 0
    except Exception:
        return 0
    
def getAllPrescenceData():
    try:
        pres = {"uid": "", "time_in": "", "time_end": "", "isInstructorPresent": ""}
        con = sqlite3.connect('allowed_students.db', isolation_level=None)
        cur = con.cursor()
        cur.execute('select uid, time_in, time_end, isInstructorPresent from inst_prescence where rowid = 1')
        row = cur.fetchone()
        pres['uid'] = row[0]; pres['time_in'] = row[1]; pres['time_end'] = row[2]; pres['isInstructorPresent'] = row[3]
        return pres
    except:
        return {"uid": "", "time_in": "", "time_end": "", "isInstructorPresent": 0}
print(getFacultyPrescenceState())