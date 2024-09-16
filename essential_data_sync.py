import json
import requests
from internetCheck import isInternetUp
import coloredlogs, logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING)
coloredlogs.install(level="DEBUG", logger=logger)
import time

def esse_sync():
    localMode = False
    BASE_API_URL = "https://www.pilocksystem.live/api/"
    if not localMode:
        enrolled_courses_bak_is_successful = False
        student_bak_is_successful = False
        faculty_bak_is_successful = False
        retries = 0
        
        while True:
            if not enrolled_courses_bak_is_successful:
                try:
                    ecs_bak = requests.get(BASE_API_URL + "enrolledcourses", timeout=2)
                    with open("backup_data/temp_enrolled.json", "w") as f:
                        json.dump(ecs_bak.json(), f)
                    logger.info("EDS: Fetched latest data from schedules for backup.")
                    enrolled_courses_bak_is_successful = True
                    #anti-file corruption bois
                    #do not write shit if the api sends blank lmao
                    if enrolled_courses_bak_is_successful:
                        with open('backup_data/temp_enrolled.json', "r")as fr, open('backup_data/enrolled_students.json', "w") as to:
                            to.write(fr.read())
                except Exception:
                    logger.critical("EDS: Blank response. Schedules data might be empty!")
            if not student_bak_is_successful:
                try:
                    ecs_bak = requests.get(BASE_API_URL + "students", timeout=2)
                    with open("backup_data/temp_students.json", "w") as f:
                        json.dump(ecs_bak.json(), f)
                    logger.info("EDS: Fetched latest data from students for backup.")
                    student_bak_is_successful = True
                    if student_bak_is_successful:
                        with open('backup_data/temp_students.json', "r")as fr, open('backup_data/students.json', "w") as to:
                            to.write(fr.read())
                except Exception:
                    logger.critical("EDS: Blank response. Students data might be empty!")
            if not faculty_bak_is_successful:
                try:
                    ecs_bak = requests.get(BASE_API_URL + "instructors", timeout=2)
                    with open("backup_data/temp_faculty.json", "w") as f:
                        json.dump(ecs_bak.json(), f)
                    logger.info("EDS: Fetched latest data from students for backup.")
                    faculty_bak_is_successful = True
                    if faculty_bak_is_successful:
                        with open('backup_data/temp_faculty.json', "r")as fr, open('backup_data/faculty.json', "w") as to:
                            to.write(fr.read())
                except Exception:
                    logger.critical("EDS: Blank response. Instructors data might be empty!")
            if (
                faculty_bak_is_successful
                and student_bak_is_successful
                and enrolled_courses_bak_is_successful
            ):
                logger.info("All backup has been completed!")
                retries = 0
                faculty_bak_is_successful = False
                student_bak_is_successful = False
                enrolled_courses_bak_is_successful = False
                break
            elif retries >= 4:
                logger.info("Backup failed after exceeding max retries. Please check the Pi-Lock web service endpoints.")
                retries = 0
                faculty_bak_is_successful = False
                student_bak_is_successful = False
                enrolled_courses_bak_is_successful = False
                break
            else:
                retries += 1
                logger.warning(
                    "Failed to backup one or more tables. Retrying in 1 second. (Retry "
                    + str(retries)
                    + " of 4)"
                )
                time.sleep(1)
    else:
        return
