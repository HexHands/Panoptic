import os
import sys
import time
import subprocess
import signal
import log

#########################

if not os.path.exists("./data"):
    os.makedirs("./data")
if not os.path.exists("./data/devices"):
    os.makedirs("./data/devices")
if not os.path.exists("./captures"):
    os.makedirs("./captures")

#########################

website = subprocess.Popen(
    ['gunicorn', '-w', '4', '-b', '0.0.0.0:8080', 'website:app'],
    preexec_fn=os.setsid
)
import webcam
webcam.start()
import erase
erase.start()

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
    print(log.l("Successfully stopped!"))