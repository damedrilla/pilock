import json
import requests
def getStudent(con_status, uid):
    localMode = con_status
    try:
        if localMode == False:
            print(uid)
            userRes = requests.get("http://152.42.167.108/api/student/" + str(uid))
            parseUser = json.loads(userRes.text)
            print(parseUser)
        else:
            students_bak = open("students.json")
            parseStuds = json.load(students_bak)
            for studs in range(len(parseStuds["students"])):
                if uid == parseStuds["students"][studs]["tag_uid"]:
                    return parseStuds["students"][studs]
    except Exception as e:
        print("first try error")