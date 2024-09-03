import json
import requests
from internetCheck import isInternetUp
from getCourseID import getCourseID
from facPrescenceController import (
    getFacultyPrescenceState,
    getAllPrescenceData,
    isStudentAllowedToEnter,
)
from timecheck import isBludNotLate
from getStudentData import getStudentData
from getEnrolledStudents import getEnrolledStudents
import datetime
import sqlite3


# The goal of this method is to make sure that regardless of
# internet connection availability, the output must be as similar
# as the one we see in this system's web API to ensure smooth
# operation during production use.
def getStudent(uid):
    localMode = isInternetUp()
    uid = str(uid).zfill(10)
    if not localMode:
        # Students registered without an ID card has a value of null in tag_uid key
        # and throws an exception if we try to compare it.
        # Try-catch block makes it sure the loop continues in case of a null tag_uid value.

        # Return codes
        # 200 -> Allowed to enter
        # 399 :tf: -> Over grace period
        # 401 -> Faculty is absent
        # 403 -> Not enrolled
        # 404 | 500 -> Not registered
        try:
            # print("auth" + str(checkIfAuthorized(uid)))
            if checkIfAuthorized(uid) == 200:
                students_list = requests.post(
                    "https://www.pilocksystem.live/api/attendstud/"
                    + uid,
                    timeout=2,
                )
                if students_list.status_code == 200:
                    return 200
                elif students_list.status_code == 401:
                    fac_prescence = getFacultyPrescenceState()
                    fac_all_data = getAllPrescenceData()
                    if fac_prescence == 1:
                        # In case that the instructor becomes present while there's no internet
                        # and the student authenticated after the internet connectivity returns back
                        try:
                            requests.post(
                                "https://www.pilocksystem.live/api/attendinst/"
                                + str(fac_all_data["uid"]).zfill(10),
                                timeout=2,
                            )
                            return 200
                        except:
                            return 401
                    else:
                        return 401
                elif students_list.status_code == 403:
                    return 403
                else:
                    return 404
            elif checkIfAuthorized(uid) == 399:
                return 399
            elif checkIfAuthorized(uid) == 403:
                return 403
            elif checkIfAuthorized(uid) == 401:
                return 401
            elif checkIfAuthorized(uid) == 500:
                return 500
        except Exception as e:
            print(e)
            return 500
        print('bottom')
        return 500
    elif localMode:
        try:
            uid = str(uid).zfill(10)
            course_id = getCourseID()
            enrolled_students = open("backup_data/enrolled_students.json")
            enrolled_students_bak = json.load(enrolled_students)
            es_data = enrolled_students_bak["enrolledCourses"]

            for _students in range(len(es_data)):
                try:
                    if (
                        uid == es_data[_students]["studentTag_uid"]
                        and course_id == es_data[_students]["course_id"]
                    ):
                        fac_prescence = open("backup_data/instructor_prescence.json")
                        fp_data = getFacultyPrescenceState()
                        if fp_data == 1:
                            try:
                                if isStudentAllowedToEnter(str(uid).zfill(10)):

                                    return 200
                                else:
                                    fac_all_data = getAllPrescenceData()
                                    curr_time = str(
                                        datetime.datetime.now()
                                        .time()
                                        .replace(microsecond=0)
                                    )
                                    is_student_on_time = isBludNotLate(
                                        curr_time, fac_all_data["time_in"]
                                    )
                                    if is_student_on_time:
                                        try:

                                            con = sqlite3.connect(
                                                "allowed_students.db",
                                                isolation_level=None,
                                            )
                                            cur = con.cursor()
                                            param = (str(uid).zfill(10),)
                                            cur.execute(
                                                "insert into authorized values (?)",
                                                param,
                                            )
                                            con.close()
                                        except:
                                            pass
                                        return 200
                                    else:
                                        return 399
                            except:
                                return 401
                        else:
                            return 401
                    else:
                        continue
                except:
                    return 404
        except Exception as e:
            return 404
        return 404


def checkIfAuthorized(uid):
    uid = str(uid)
    # if isStudentEnrolled(uid) == 500:
    #     return 500
    # elif isStudentEnrolled(uid) == 403:
    #     return 403
    if isStudentAllowedToEnter(str(uid).zfill(10)):
        print('already in database!')
        return 200
    else:
        fac_all_data = getAllPrescenceData()
        if fac_all_data['isInstructorPresent'] == 0:
            return 401
        curr_time = str(datetime.datetime.now().time().replace(microsecond=0))
        if isBludNotLate(curr_time, fac_all_data["time_in"]):
            try:
                con = sqlite3.connect("allowed_students.db", isolation_level=None)
                cur = con.cursor()
                param = (uid,)
                cur.execute("insert into authorized values (?)", param)
                con.close()
            except:
                pass
            return 200
        else:
            return 399


# def isStudentEnrolled(uid):
#     course_id = getCourseID()
#     data = getStudentData(uid)
#     enrolled_stud = getEnrolledStudents()
#     if data["status"] == 404:
#         return 500
#     try:
#         if enrolled_stud["status"] == 404:
#             return 404
#     except:
#         pass
#     for _students in range(len(enrolled_stud)):
#         try:
#             if (
#                 uid == enrolled_stud[_students]["studentTag_uid"]
#                 and course_id == enrolled_stud[_students]["course_id"]
#             ):
#                 return 200
#         except Exception as e:
#             print(e)
#             continue
#     return 403
