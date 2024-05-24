from datetime import datetime
import os
import json
import webcam
import log
import threading
import time
import sys
import subprocess
import requests

#########################

erasefilepath = "./data/erase.json"
argvfilepath = "./data/argv.json"

#########################

def scanfiles():
	data = []
	for device in os.listdir("./captures"):
		for day in os.listdir(f"./captures/{device}"):
			for capture in os.listdir(f"./captures/{device}/{day}"):
				filepath = f"./captures/{device}/{day}/{capture}"
				data.append({"filepath": filepath, "size": os.path.getsize(filepath), "date": os.path.splitext(os.path.basename(filepath))[0]})
	return data

def totalsize(data):
	size = 0
	for file in data:
		size += file["size"]
	return size

def eraseold():
	def parsedate(item):
		return datetime.strptime(item['date'], "%Y-%m-%d %H:%M:%S")

	systemsettings = webcam.getsetting()

	data = sorted(scanfiles(), key=parsedate)
	currentsize = totalsize(data)
	currentsize = currentsize / (1 << 30)
	while currentsize > systemsettings["disksize"] - 1:
		try:
			print(log.l(f"ERASE: erase.py > eraseold > Erased file at {data[0]['filepath']} with a size of {data[0]['size'] / (1 << 30)}GB."))
			currentsize -= data[0]["size"]
			os.remove(data[0]["filepath"])
			folder = os.path.dirname(data[0]["filepath"])
			if len(os.listdir(folder)) == 0:
				print(log.l("ERASE: erase.py > eraseold > Deleted folder {folder}."))
				os.rmdir(folder)
			data.pop(0)
		except Exception as e:
			print(log.l(f"ERROR: erase.py > eraseold > {e}"))

#########################

def mainerase():
	global erasefilepath
	global argvfilepath

	systemsettings = webcam.getsetting()
	if not os.path.exists(erasefilepath):
		with open(erasefilepath, "w") as file:
			file.write(json.dumps({"lasterased": 0, "lastreboot": time.time()}))

	with open(erasefilepath, "r") as file:
		data = json.load(file)

	if data["lasterased"] < time.time() - int(systemsettings["erasefrequency"]) * 60 * 60:
		print(log.l("ERASE: erase.py > mainerase > Checking for possible erase jobs."))
		eraseold()
		data["lasterased"] = time.time()
		data.update(data)
		with open(erasefilepath, "w") as file:
			file.write(json.dumps(data, indent=2))

	if data["lastreboot"] < time.time() - int(systemsettings["autoreboot"]) * 60 * 60 and systemsettings.get("endireboot", True):
		print(log.l("REBOOT: erase.py > mainerase > 60 second countdown till auto reboot."))
		data.update({"lastreboot": time.time()})
		with open(erasefilepath, "w") as file:
			file.write(json.dumps(data, indent=2))
		time.sleep(60)
		print(log.l("REBOOT: erase.py > mainerase > Auto rebooting system."))

		with open(argvfilepath, "r") as file:
			argvs = json.load(file)

		response = requests.put(f"http://localhost:{argvs.get('port', '8080')}/reboot", timeout=5, cookies={"password": systemsettings.get("password", "")})

		print(log.l(f"REBOOT: erase.py > mainerase > Reboot requested with code {response.status_code} and response {response.json()['message']}."))

		#subprocess.run("reboot")

#########################

stopthread = False

def main():
	global stopthread
	global erasefilepath

	if os.path.exists(erasefilepath):
		try:
			with open(erasefilepath, "w") as file:
				data = json.load(file)
				data.update({"lastreboot": time.time()})
				file.write(json.dumps(data, indent=2))
		except:
			with open(erasefilepath, "w") as file:
				data = {"lasterased": 0, "lastreboot": time.time()}
				file.write(json.dumps(data, indent=2))
	else:
		with open(erasefilepath, "w") as file:
			file.write(json.dumps({"lasterased": 0, "lastreboot": time.time()}))

	while True:
		if stopthread:
			sys.exit(0)

		time.sleep(1)
		try:
			mainerase()
		except Exception as e:
			print(log.l(f"REBOOT: erase.py > main > {e}"))

def start():
	thread = threading.Thread(target=main)
	thread.start()

def stop():
	global stopthread
	stopthread = True

#########################