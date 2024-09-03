import requests
import json
from internetCheck import isInternetUp

def getEnrolledStudents():
    conn_status = False
    if conn_status:
        try:
            data = requests.get('https://www.pilocksystem.live/api/enrolledcourses', timeout=2)
            data_js = json.loads(data.text)
            data_parsed = data_js['enrolledCourses']
            return data_parsed
        except Exception as e:
            print(e)
            return {"status": 404}
    else:
        try:
            data = open("backup_data/enrolled_students.json")
            data_js = json.load(data)
            data_parsed = data_js["enrolledCourses"]
            return data_parsed
        except:
            return {"status": 404}
