from getCurrentSchedule import currentSchedule
import json

def trim_dict():
    base_dict = currentSchedule()
    updated_dict = {}
    try:
        updated_dict["course_title"] = base_dict["course_title"]
        updated_dict["instructor"] = base_dict["instructor"]
        updated_dict["section"] = base_dict["section"]
        return updated_dict
    except Exception as e:
        return {"status": "nothing 💀"}

def getCourseID():
    c_sched_trimmed = trim_dict()
    try:
        courses_bak = open('backup_data/courses.json')
        courses_bak_json = json.load(courses_bak)
        c_data = courses_bak_json['courses']
        for _data in range(len(c_data)):
            if (c_data[_data]['course_title'] == c_sched_trimmed['course_title'] 
                and c_data[_data]['instructor'] == c_sched_trimmed['instructor'] 
                and c_data[_data]['section'] == c_sched_trimmed['section'] ):
                return c_data[_data]["id"]
            else:
                return -1
    except Exception as e:
        return -1