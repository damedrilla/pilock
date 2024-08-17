import requests
from internetCheck import isInternetUp
import coloredlogs, logging
import json
import time

logger = logging.getLogger(__name__)
logging.basicConfig(filename="pilock.log", encoding="utf-8", level=logging.INFO)
coloredlogs.install(level="DEBUG", logger=logger)


# For every :00 minute of hour, fetch the latest data from the cloud for backup.
def backup():
    BASE_API_URL = "https://www.pilocksystem.live/api/"
    localMode = isInternetUp()
    if localMode == False:
        retries = 0
        sched_bak_is_successful = False
        faculty_bak_is_successful = False
        student_bak_is_successful = False
        event_bak_is_successful = False
        make_up_bak_is_successful = False
        courses_bak_is_successful = False
        enrolled_courses_bak_is_successful = False

        while True:
            if not sched_bak_is_successful:
                try:
                    schedres = requests.get(BASE_API_URL + "schedules", timeout=2)
                    with open("backup_data/schedules.json", "w") as f:
                        json.dump(schedres.json(), f)
                    logger.info("Fetched latest data from schedules for backup.")
                    sched_bak_is_successful = True
                except Exception:
                    logger.critical("Blank response. Schedules data might be empty!")
            if not faculty_bak_is_successful:
                try:
                    facultyres = requests.get(BASE_API_URL + "instructors", timeout=2)
                    with open("backup_data/faculty.json", "w") as f:
                        json.dump(facultyres.json(), f)
                    logger.info("Fetched latest data from instructors for backup.")
                    faculty_bak_is_successful = True
                except Exception:
                    logger.critical("Blank response. Faculty data might be empty!")
            if not student_bak_is_successful:
                try:
                    studentres = requests.get(BASE_API_URL + "students", timeout=2)
                    with open("backup_data/students.json", "w") as f:
                        json.dump(studentres.json(), f)
                    logger.info("Fetched latest data from students for backup.")
                    student_bak_is_successful = True
                except Exception:
                    logger.critical("Blank response. Students data might be empty!")
            if not event_bak_is_successful:
                try:
                    eventres = requests.get(BASE_API_URL + "events", timeout=2)
                    with open("backup_data/events.json", "w") as f:
                        json.dump(eventres.json(), f)
                    logger.info("Fetched latest data from events for backup.")
                    event_bak_is_successful = True
                except Exception:
                    logger.critical("Blank response. Events data might be empty!")
            if not make_up_bak_is_successful:
                try:
                    makeup_sch = requests.get(BASE_API_URL + "makeupscheds", timeout=2)
                    with open("backup_data/makeupclass.json", "w") as f:
                        json.dump(makeup_sch.json(), f)
                    logger.info(
                        "Fetched latest data from make-up schedules for backup."
                    )
                    make_up_bak_is_successful = True
                except Exception:
                    logger.critical(
                        "Blank response. Make-up class schedules data might be empty!"
                    )
            if not courses_bak_is_successful:
                try:
                    courses_bak = requests.get(BASE_API_URL + "courses", timeout=2)
                    with open("backup_data/courses.json", "w") as f:
                        json.dump(courses_bak.json(), f)
                        logger.info("Fetched latest data from courses for backup")
                        courses_bak_is_successful = True
                except:
                    logger.critical("Blank response. Courses data might be empty!")
            if not enrolled_courses_bak_is_successful:
                try:
                    ecs_bak = requests.get(BASE_API_URL + "enrolledcourses", timeout=2)
                    with open("backup_data/enrolled_students.json", "w") as f:
                        json.dump(ecs_bak.json(), f)
                        logger.info(
                            "Fetched latest data from enrolled students for backup"
                        )
                        enrolled_courses_bak_is_successful = True
                except:
                    logger.critical(
                        "Blank response. Enrolled students data might be empty!"
                    )

            if (
                sched_bak_is_successful
                and faculty_bak_is_successful
                and student_bak_is_successful
                and event_bak_is_successful
                and make_up_bak_is_successful
                and courses_bak_is_successful
                and enrolled_courses_bak_is_successful
            ):
                logger.info("All backup has been completed!")
                retries = 0
                sched_bak_is_successful = False
                faculty_bak_is_successful = False
                student_bak_is_successful = False
                event_bak_is_successful = False
                make_up_bak_is_successful = False
                courses_bak_is_successful = False
                enrolled_courses_bak_is_successful = False
                break
            elif retries >= 4:
                logger.critical(
                    "Backup failed after exceeding max retries. Please check the Pi-Lock web service endpoints."
                )
                retries = 0
                sched_bak_is_successful = False
                faculty_bak_is_successful = False
                student_bak_is_successful = False
                event_bak_is_successful = False
                make_up_bak_is_successful = False
                courses_bak_is_successful = False
                enrolled_courses_bak_is_successful = False
                break
            else:
                retries += 1
                logger.warning(
                    "Failed to backup one or more tables. Retrying in 5 seconds. (Retry "
                    + str(retries)
                    + " of 4)"
                )
                time.sleep(5)
    else:
        return

backup()