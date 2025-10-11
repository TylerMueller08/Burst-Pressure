import datetime
import time

def currentDatestamp():
    return datetime.datetime.now().strftime("%m-%d-%Y_%H-%M-%S")

def perfTime():
    return time.perf_counter()