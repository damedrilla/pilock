# Time Check Algorithm
# Time checking modules in the web sucks so why not make my own amrite? ¯\_(ツ)_/¯
import datetime

def isThisTheTime(time_in, time_out, curr_time):
    startArr = time_in.split(':')
    endArr = time_out.split(':')
    currArr = curr_time.split(':')
    
    startTime = datetime.time(int(startArr[0]), int(startArr[1]), int(startArr[2]))
    endTime = datetime.time(int(endArr[0]), int(endArr[1]), int(endArr[2]))
    currTime = datetime.time(int(currArr[0]), int(currArr[1]), int(currArr[2]))
    
    return startTime <= currTime <= endTime