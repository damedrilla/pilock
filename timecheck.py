# Time Check Algorithm
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
        time_end = str(kwargs.get("time_end")).split(":")
        currArr = str(kwargs.get("currTime")).split(":")

        endTime = datetime.time(int(time_end[0]), int(time_end[1]), int(time_end[2]))
        currTime = datetime.time(int(currArr[0]), int(currArr[1]), int(currArr[2]))

        return currTime >= endTime
    else:
        # If we only want to check the time only, we go here.
        startArr = time_in.split(":")
        endArr = time_out.split(":")
        currArr = curr_time.split(":")

        startTime = datetime.time(int(startArr[0]), int(startArr[1]), int(startArr[2]))
        endTime = datetime.time(int(endArr[0]), int(endArr[1]), int(endArr[2]))
        currTime = datetime.time(int(currArr[0]), int(currArr[1]), int(currArr[2]))

        return startTime <= currTime <= endTime
