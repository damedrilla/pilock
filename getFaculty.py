import requests
import json
def getFaculty(conn_status, uid):
    if not conn_status:
        try:
            instructor_list = requests.get("https://www.pilocksystem.live/api/instructors")
            inst = json.loads(instructor_list.text)
            for instr in range(len(inst["instructors"])):
                uuid = inst["instructors"][instr]["tag_uid"]
                uid_no_lead = int(uuid)
                # print(uid_no_lead)
                if str(uid) == str(uid_no_lead):
                    return inst["instructors"][instr]
        except Exception as e:
            return {'status': 404}
    else:
        try:
            faculty_bak = open('faculty.json')
            inst = json.load(faculty_bak)
            for instr in range(len(inst["instructors"])):
                uuid = inst["instructors"][instr]["tag_uid"]
                uid_no_lead = int(uuid)
                # print(uid_no_lead)
                if str(uid) == str(uid_no_lead):
                    return inst["instructors"][instr]
        except Exception as e:
            return {'status': 404}


# x = getFaculty(True, 1234567891)
# y = getFaculty(False, 1234567891)

# print(x)
# print(y)