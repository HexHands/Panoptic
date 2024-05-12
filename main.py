import os
import sys
import time
import subprocess
import signal
import json

#########################

def unpackargv():
    args = sys.argv[1:]
    result_dict = {}
    for arg in args:
        parts = arg.split(':')
        if len(parts) != 2:
            print(f"Invalid format for argument {arg}.")
            return None
        result_dict[parts[0]] = parts[1]
    return result_dict

os.chdir(unpackargv().get("path", "./"))

#########################

import log
print(log.l("SYSTEM: main.py > > Started Panoptic."))

#########################

if not os.path.exists("./data"):
    os.makedirs("./data")
if not os.path.exists("./data/devices"):
    os.makedirs("./data/devices")
if not os.path.exists("./captures"):
    os.makedirs("./captures")
with open("./data/argv.json", "w") as file:
    file.write(json.dumps(unpackargv(), indent=2))

#########################

website = subprocess.Popen(
    ['gunicorn', '-w', '4', '-b', f'0.0.0.0:{unpackargv().get("port", "8080")}', 'website:app'],
    preexec_fn=os.setsid
)
import webcam
webcam.start()
import erase
erase.start()

print(log.l("SYSTEM: main.py > > Started subsystems."))

#########################

def line():
    print("#" * 25)

#########################

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print(log.l("Interrupt received, stopping..."))
finally:
    os.killpg(os.getpgid(website.pid), signal.SIGTERM)
    webcam.stop()
    erase.stop()
    print(log.l("SYSTEM: main.py > > Successfully stopped!"))