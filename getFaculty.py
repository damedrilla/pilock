import requests
import json
from internetCheck import isInternetUp


def getFaculty(uid):
    localMode = isInternetUp()
    if not localMode:
        try:
            instructor_list = requests.get(
                "https://www.pilocksystem.live/api/instructors", timeout=2
            )
            inst = json.loads(instructor_list.text)
            for instr in range(len(inst["instructors"])):
                try:
                    uuid = inst["instructors"][instr]["tag_uid"]
                    uid_no_lead = int(uuid)
                    # print(uid_no_lead)
                    if str(uid) == str(uid_no_lead):
                        return inst["instructors"][instr]
                except Exception:
                    continue
        except Exception as e:
            return {"status": 404}
    else:
        try:
            faculty_bak = open("backup_data/faculty.json")
            inst = json.load(faculty_bak)
            for instr in range(len(inst["instructors"])):
                try:
                    uuid = inst["instructors"][instr]["tag_uid"]
                    uid_no_lead = int(uuid)
                    # print(uid_no_lead)
                    if str(uid) == str(uid_no_lead):
                        return inst["instructors"][instr]
                except Exception:
                    continue
        except Exception as e:
            return {"status": 404}


# x = getFaculty(True, 1234567891)
# y = getFaculty(False, 1234567891)

# print(x)
# print(y)
