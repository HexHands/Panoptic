import os
from datetime import datetime

#########################

LOG_DIR = "./data"
LOG_FILE1 = os.path.join(LOG_DIR, "log1.txt")
LOG_FILE2 = os.path.join(LOG_DIR, "log2.txt")
LOG_STATE_FILE = os.path.join(LOG_DIR, "logstate.txt")

def initialize_log_system():
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    for file_path in [LOG_FILE1, LOG_FILE2, LOG_STATE_FILE]:
        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                pass

    if os.path.getsize(LOG_STATE_FILE) == 0:
        with open(LOG_STATE_FILE, "w") as f:
            f.write(LOG_FILE1)

def write_log(text):
    initialize_log_system()
    with open(LOG_STATE_FILE, "r") as f:
        current_log = f.read().strip()

    try:
        with open(current_log, "a") as log_file:
            log_file.write(text + "\n")

        if os.path.getsize(current_log) > 1048576: #1MB
            next_log = LOG_FILE2 if current_log == LOG_FILE1 else LOG_FILE1
            with open(next_log, "w") as f:
                pass
            with open(LOG_STATE_FILE, "w") as f:
                f.write(next_log)
    except Exception as e:
        next_log = LOG_FILE2 if current_log == LOG_FILE1 else LOG_FILE1
        with open(next_log, "w") as f:
            pass
        with open(LOG_STATE_FILE, "w") as f:
            f.write(next_log)
        write_log(text)

def read_logs():
    initialize_log_system()
    logs = []
    for log_file in [LOG_FILE1, LOG_FILE2]:
        with open(log_file, "r") as file:
            logs.extend(file.readlines())
    logs.reverse()
    return logs

#########################

def l(data, time=True, file_path="./data/log.txt", max_size=1048576):
    data = str(data)

    if time:
        data = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " + data
    else:
        data = data

    write_log(data)
    return data

#########################