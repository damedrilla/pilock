import requests
import json
from internetCheck import isInternetUp

def getEnrolledStudents():
    try:
        data = open("backup_data/enrolled_students.json")
        data_js = json.load(data)
        data_parsed = data_js["enrolledCourses"]
        return data_parsed
    except:
        return {"status": 404}
