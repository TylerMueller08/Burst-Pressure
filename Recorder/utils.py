import datetime

def currentTimestamp():
    return datetime.datetime.now().strftime("%H:%M:%S.%f")[:-4]

def currentDatestamp():
    return datetime.datetime.now().strftime("%m-%d-%Y_%H-%M-%S")