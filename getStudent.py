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
        
        #Return codes
        #200 -> Allowed to enter 
        #401 -> Faculty is absent
        #403 -> Not enrolled
        #404 | 500 -> Not registered
        try:
            students_list = requests.post("https://www.pilocksystem.live/api/attendstud/" +  str(uid), timeout= 2)
            if students_list.status_code == 200:
                return 200
            elif students_list.status_code == 401:
                fac_prescence = open('backup_data/instructor_prescence.json')
                fp_data = json.loads(fac_prescence)
                if fp_data['isInstructorPresent'] == 1:
                    #In case that the instructor becomes present while there's no internet
                    #and the student authenticated after the internet connectivity returns back 
                    try:
                        requests.post('https://www.pilocksystem.live/api/inst/' + str(fp_data['uid']).zfill(10), timeout=2)
                    except:
                        pass
                    return 200
                else:
                    return 401
            elif students_list.status_code == 403:
                return 403
            else:
                return 404
        except Exception as e:
            print(e)
            return 500
    elif localMode:
        try:
            uid = str(uid).zfill(10)
            course_id = getCourseID()
            enrolled_students = open('backup_data/enrolled_students.json')
            enrolled_students_bak = json.load(enrolled_students)
            es_data = enrolled_students_bak['enrolledCourses']
            
            for _students in range(len(es_data)):
                if uid == es_data[_students]['studentTag_uid'] and course_id == es_data[_students]['course_id']:
                    fac_prescence = open('backup_data/instructor_prescence.json')
                    fp_data = json.loads(fac_prescence)
                    if fp_data['isInstructorPresent'] == 1:
                        return 200
                    else:
                        return 401
                else:
                    return 404
        except Exception as e:
            return 404

