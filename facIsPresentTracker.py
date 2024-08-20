from getCurrentSchedule import currentSchedule
from internetCheck import localMode
from timecheck import timeCheck
from datetime import datetime
import json
import time


def tracker():
    while True:
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        try:
            state = open("backup_data/instructor_prescence.json")
            parsed_state = json.load(state)
            curr_sched = currentSchedule()
            curr_sched_end = curr_sched["time_end"]
            _end = parsed_state["time_end"]
            isCurrentScheduleOver = timeCheck(
                "", "", "", time_end=_end, currTime=current_time
            )
            if isCurrentScheduleOver:
                data = {"time_end": curr_sched_end, "isInstructorPresent": 0}
                with open("backup_data/instructor_prescence.json", "w") as f:
                    json.dump(data, f)
                    f.close()
            time.sleep(1)
            state.close()
        except Exception as e:
            time.sleep(1)
            state.close()
