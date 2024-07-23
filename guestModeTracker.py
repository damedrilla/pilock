from getCurrentSchedule import currentSchedule
from internetCheck import localMode
guestMode = False

def guestMode_QuestionMark():
    global guestMode
    currSched = currentSchedule(localMode)
    try:
        if currSched["sched_type"] == "Event":
            guestMode = True
        else:
            guestMode = False
    except Exception:
        guestMode = False
