import json
import requests
from internetCheck import isInternetUp
from getCourseID import getCourseID

# The goal of this method is to make sure that regardless of 
# internet connection availability, the output must be as similar
# as the one we see in this system's web API to ensure smooth
# operation during production use.
def getStudentData(uid):
    uid = str(uid)
    localMode = isInternetUp()
    if not localMode:
        # Students registered without an ID card has a value of null in tag_uid key
        # and throws an exception if we try to compare it.
        # Try-catch block makes it sure the loop continues in case of a null tag_uid value.
        try:
            students_list = requests.get("https://www.pilocksystem.live/api/students", timeout= 2)
            stud_json = json.loads(students_list.text)
            for index in range(len(stud_json["students"])):
                try:
                    uuid = stud_json["students"][index]["tag_uid"]
                    # remove leading zeroes again askljdbhsdhgasd
                    uid_no_lead = int(uuid)
                    if str(uid) == str(uid_no_lead):
                        stud_data = stud_json["students"][index]
                        stud_data['status'] = 200
                        return stud_data
                except Exception:
                    continue
        except Exception as e:
            return {"status": 404}
    elif localMode:
        try:
            stud_bak = open("backup_data/students.json")
            stud_json = json.load(stud_bak)
            for index in range(len(stud_json["students"])):
                try:
                    uuid = stud_json["students"][index]["tag_uid"]
                    uid_no_lead = int(uuid)
                    # print(uid_no_lead)
                    if str(uid) == str(uid_no_lead):
                        stud_data = stud_json["students"][index]
                        stud_data['status'] = 200
                        return stud_data
                except Exception:
                    continue
        except Exception as e:
            print(e)
            return {"status": 404}
    return {"status": 404}