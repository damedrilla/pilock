from getCurrentSchedule import currentSchedule
from internetCheck import internetCheck
guestMode = False

def guestMode_QuestionMark():
    global guestMode
    currSched = currentSchedule()
    try:
        if currSched["sched_type"] == "Event":
            guestMode = True
        else:
            guestMode = False
    except Exception:
        guestMode = False
