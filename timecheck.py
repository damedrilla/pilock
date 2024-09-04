# Time Checking Algorithm
import datetime


# Time in, time out, and current time is guaranteed to have value. The optional values
# is the date in case of events and make-up classes.
def timeCheck(time_in, time_out, curr_time, **kwargs):
    if "date_scheduled" in kwargs:
        # Use this when we want to check time AND date
        date_scheduled = kwargs.get("date_scheduled")
        date_today = str(datetime.datetime.now().date())

        # The classic
        startArr = time_in.split(":")
        endArr = time_out.split(":")
        currArr = curr_time.split(":")

        startTime = datetime.time(int(startArr[0]), int(startArr[1]), int(startArr[2]))
        endTime = datetime.time(int(endArr[0]), int(endArr[1]), int(endArr[2]))
        currTime = datetime.time(int(currArr[0]), int(currArr[1]), int(currArr[2]))

        # Both true means true, otherwise false
        return (date_today == date_scheduled) and (startTime <= currTime <= endTime)
    elif "time_end" in kwargs:
        try:
            if str(kwargs.get("time_end")) == "":
                return True
            
            time_end = str(kwargs.get("time_end")).split(":")
            currArr = str(kwargs.get("currTime")).split(":")

            endTime = datetime.time(int(time_end[0]), int(time_end[1]), int(time_end[2]))
            currTime = datetime.time(int(currArr[0]), int(currArr[1]), int(currArr[2]))

            return currTime >= endTime
        except:
            return True
    else:
        # If we only want to check the time only, we go here.
        startArr = time_in.split(":")
        endArr = time_out.split(":")
        currArr = curr_time.split(":")

        startTime = datetime.time(int(startArr[0]), int(startArr[1]), int(startArr[2]))
        endTime = datetime.time(int(endArr[0]), int(endArr[1]), int(endArr[2]))
        currTime = datetime.time(int(currArr[0]), int(currArr[1]), int(currArr[2]))

        return startTime <= currTime <= endTime

#https://stackoverflow.com/questions/100210/what-is-the-standard-way-to-add-n-seconds-to-datetime-time-in-python
def addSecs(tm, secs):
    fulldate = datetime.datetime(100, 1, 1, tm.hour, tm.minute, tm.second)
    fulldate = fulldate + datetime.timedelta(seconds=secs)
    return fulldate.time()


def isBludNotLate(stud_scan_time, faculty_log_in_time):
    try:
        scan_time_arr = stud_scan_time.split(":")
        log_in_time_arr = faculty_log_in_time.split(":")
        
        scan_time = datetime.time(int(scan_time_arr[0]), int(scan_time_arr[1]), int(scan_time_arr[2]))
        log_in_time = datetime.time(int(log_in_time_arr[0]), int(log_in_time_arr[1]), int(log_in_time_arr[2]))
        xv_mins = 60 * 30
        xv_mins_after = addSecs(log_in_time, xv_mins)
        return scan_time <= xv_mins_after
    except:
        return False
    