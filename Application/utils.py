import os, time, csv
from datetime import datetime

def timestamp(format="%m-%d-%Y_%H-%M-%S"):
    return datetime.now().strftime(format)

def elapsed(start_time):
    return time.perf_counter() - start_time

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def create_csv(prefix, headers):
    results_dir = "data"
    ensure_dir(results_dir)

    filename = os.path.join(results_dir, f"{prefix}_{timestamp()}.csv")
    file = open(filename, "w", newline="")
    writer = csv.writer(file)
    writer.writerow(headers)
    log("Data Logger", f"Created file: {filename}")
    return file, writer

def log(tag, message):
    print(f"[{tag} | {timestamp("%H:%M:%S")}] {message}")
