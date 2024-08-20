from getCurrentSchedule import currentSchedule
from internetCheck import internetCheck

def guestMode_QuestionMark():
    guestMode = False
    currSched = currentSchedule()
    print(str(currSched))
    try:
        if currSched["sched_type"] == "Event":
            guestMode = True
        else:
            guestMode = False
    except Exception:
        guestMode = False
    return guestMode
