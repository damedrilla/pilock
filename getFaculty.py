import requests
import json
from internetCheck import isInternetUp


def getFaculty(uid):
    localMode = isInternetUp()
    uid = str(uid).zfill(10)
    if not localMode:
        try:
            instructor_list = requests.get(
                "https://pilocksystem.live/api/faculty/" + uid, timeout=2
            )
            inst = json.loads(instructor_list.text)
            try:
                # print(uid_no_lead)
                return inst["faculty"][0]
            except Exception as e:
                return {"status": 404}
        except Exception as e:
            return {"status": 404}
    else:
        try:
            faculty_bak = open("backup_data/faculty.json")
            inst = json.load(faculty_bak)
            for instr in range(len(inst["faculties"])):
                try:
                    uuid = inst["faculties"][instr]["tag_uid"]
                    uid_no_lead = int(uuid)
                    # print(uid_no_lead)
                    if str(uid) == str(uid_no_lead):
                        return inst["faculties"][instr]
                except Exception:
                    continue
        except Exception as e:
            return {"status": 404}


# x = getFaculty(False, 2194764747)
# y = getFaculty(False, 1234567891)

# print(x)
# print(y)
