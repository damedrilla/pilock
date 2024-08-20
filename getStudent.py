import json
import requests
from internetCheck import isInternetUp
from getCourseID import getCourseID

# The goal of this method is to make sure that regardless of 
# internet connection availability, the output must be as similar
# as the one we see in this system's web API to ensure smooth
# operation during production use.
def getStudent(uid):
    localMode = isInternetUp()
    if not localMode:
        # Students registered without an ID card has a value of null in tag_uid key
        # and throws an exception if we try to compare it.
        # Try-catch block makes it sure the loop continues in case of a null tag_uid value.
        try:
            students_list = requests.post("https://www.pilocksystem.live/api/attendstud/" +  str(uid), timeout= 2)
            if students_list.status_code == 200:
                return {'status': 200}
            elif students_list.status_code == 401:
                return {'status': 401}
            elif students_list.status_code == 403:
                return {'status': 403}
            else:
                return {'status': 404}
        except Exception as e:
            print(e)
            return {"status": 500}
    elif localMode:
        try:
            course_id = getCourseID()
            enrolled_students = open('backup_data/enrolled_students.json')
            enrolled_students_bak = json.load(enrolled_students)
            es_data = enrolled_students_bak['enrolledCourses']
            
            for _students in range(len(es_data)):
                if uid == es_data[_students]['studentTag_uid'] and course_id == es_data[_students]['course_id']:
                    return {'status': 200}
                else:
                    return {'status': 404}
        except Exception as e:
            return {"status": 404}

print(getStudent(8878888))