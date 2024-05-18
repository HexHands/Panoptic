import threading
import time
import os
import subprocess
import json
from datetime import datetime
import log
import signal
import sys

#########################

basedata = {
	"device": "",
	"name": "",
	"videonode": None,
	"audionode": None,
	"active": False,
	"width": 480,
	"height": 360,
	"framerate": 30,
	"recordinglength": 600
}
basesettingsdata = {
	"disksize": 20,
	"erasefrequency": 24,
	"password": "panopticsystem",
	"autoreboot": 24,
	"endireboot": True
}
sessiondevices = {}

#########################

if not os.path.exists("./data/setting.json"):
	with open("./data/setting.json", "w") as file:
		file.write(json.dumps(basesettingsdata, indent=2))

#########################

def devicenodes(): #sudo apt-get install v4l-utils
	try:
		data = subprocess.run("v4l2-ctl --list-devices", shell=True, capture_output=True, text=True).stdout.strip().split("\n")
		usbnodes = {}
		lastkey = ""

		for datai in data:
			if datai != "":
				if datai.startswith("\t"):
					usbnodes[lastkey].append(datai.strip())
				else:
					lastkey = ' '.join([part.strip() for part in datai.split('(')[0:-1]]).strip()
					usbnodes[lastkey] = []

		with open("./data/devicenodes.json", "w") as json_file:
			json_file.write(json.dumps(usbnodes, indent=2))

		return usbnodes
	except Exception as e:
		print(log.l(f"ERROR: webcam.py > devicenodes > {e}"))
		return {}

#########################

def devicedata(usbnodes):
	try:
		for device in usbnodes.keys():
			path = f"./data/devices/{device}.json"
			if not os.path.exists(path):
				with open(path, "w") as json_file:
					basedata["device"] = device
					basedata["name"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
					json_file.write(json.dumps(basedata, indent=2))
	except Exception as e:
		print(log.l(f"ERROR: webcam.py > devicedata > {e}"))

def getdevicedata(device):
	path = f"./data/devices/{device}.json"
	if os.path.exists(path):
		with open(path, "r") as file:
			try:
				data = json.load(file)
			except Exception as e:
				log.l(f"ERROR: webcam.py > getdevicedata > {e}")
				data = basedata
				with open(path, "w") as file:
					file.write(json.dumps(data, indent=2))
	else:
		data = {}
	return data

def getdevicenodes(device):
	path = f"./data/devicenodes.json"
	if os.path.exists(path):
		with open(path, "r") as file:
			try:
				data = json.load(file)
			except Exception as e:
				log.l(f"ERROR: webcam.py > getdevicenodes > {e}")
	else:
		data = {}
	data = data.get(device, [])
	return data

def writedevicedata(device, datawrite):
	path = f"./data/devices/{device}.json"
	if os.path.exists(path):
		with open(path, "r") as file:
			data = json.load(file)
		data.update(datawrite)
		with open(path, "w") as file:
			file.write(json.dumps(data, indent=2))
	else:
		data = {}
	return data

def getsetting():
	path = "./data/setting.json"
	if os.path.exists(path):
		try:
			with open(path, "r") as file:
				data = json.load(file)
		except Exception as e:
			log.l(f"ERROR: webcam.py > getsetting > {e}")
			data = basesettingsdata
			with open(path, "w") as file:
				file.write(json.dumps(data, indent=2))
	else:
		data = {}
	return data

def writesetting(datawrite):
	path = f"./data/setting.json"
	if os.path.exists(path):
		with open(path, "r") as file:
			data = json.load(file)
		data.update(datawrite)
		with open(path, "w") as file:
			file.write(json.dumps(data, indent=2))
	else:
		data = {}
	return data

#########################

def operate(usbnodes):
	for device in usbnodes.keys():
		if device not in sessiondevices and getdevicedata(device)["active"]:

			stop = threading.Event()
			thread = threading.Thread(target=webcam, args=(stop, device))

			sessiondevices[device] = {
				"thread": thread,
				"stop": stop
			}

			thread.start()
	for device in sessiondevices.keys():
		if not getdevicedata(device)["active"]:
			stopdevice(device)

def stopdevicethread(device):
	if device in sessiondevices:
		if not sessiondevices[device]["stop"].is_set():
			print(log.l(f"Waiting for {device} to stop..."))
			sessiondevices[device]["stop"].set()
			sessiondevices[device]["thread"].join()
			del sessiondevices[device]
			print(log.l(f"{device} thread has been stopped!"))
	else:
		print(log.l(f"WARNING: webcam.py > stopdevicethread > {device} thread could not be stopped."))

def stopalldevicethread():
	print(log.l(f"Safe shutdown initialized for all devices."))
	for device in sessiondevices:
		if not sessiondevices[device]["stop"].is_set():
			sessiondevices[device]["stop"].set()

def stopdevice(device):
	thread = threading.Thread(target=stopdevicethread, args=(device,))
	thread.start()

#########################

def webcam(stop, device):
	print(log.l(f"{device} thread has started."))
	while not stop.is_set():
		try:
			data = getdevicedata(device)
			nodes = getdevicenodes(device)
			print(log.l(f"{device} has started recording..."))
			command = [
				"ffmpeg",
				"-y",
				"-framerate", str(data['framerate'])
			]
			if data["videonode"] == None and data["audionode"] == None:
				print(log.l(f"WARNING: webcam.py > webcam > {device} has no video/audio nodes."))
				time.sleep(5)
				continue
			if data["videonode"] != None:
				finddefault = 0
				while data["videonode"] == "Default":
					if finddefault > len(nodes):
						print(l.log(f"WARNING: webcam.py > webcam > {device} found no default video nodes."))
					if "video" in nodes[finddefault]:
						data["videonode"] = nodes[finddefault]
					finddefault += 1
					
				if data["videonode"] != "Default":
					command.extend(["-video_size", f"{data['width']}x{data['height']}", "-i", data['videonode']])
			command.extend([
				"-c:v", "libx264",
				"-t", str(data["recordinglength"]),
				f"./captures/{device}/{datetime.now().strftime('%Y-%m-%d')}/{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.mp4"])
			if data["audionode"] != None:
				if data["videonode"] == None:
					print(log.l(f"WARNING: webcam.py > webcam > {device} has no video node is required to record audio."))
					time.sleep(5)
					continue
				command.extend(["-f", "alsa", "-i", data['audionode'].lower()])

			capture_directory = f"./captures/{device}/{datetime.now().strftime('%Y-%m-%d')}"
			if not os.path.isdir(capture_directory):
				os.makedirs(capture_directory)

			with open(f"./data/{device}-log.txt", "w+") as file:
				process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=file, text=True)
				while True:
				    if process.poll() is not None:
				        break
				    if stop.is_set():
				        process.send_signal(signal.SIGINT)
				        break
				    time.sleep(0.5)

				process.wait()
				file.seek(0)
				stderr = file.read()

			if process.returncode != 0:
				print(log.l(f"ERROR: webcam.py > webcam > {stderr}"))
				time.sleep(5)
				continue
			else:
				print(log.l(f"{device} has finished recording successfully."))
		except Exception as e:
			print(log.l(f"ERROR: webcam.py > webcam > {e}"))

#########################

stopthread = False

def main():
	global stopthread

	while True:
		if stopthread:
			sys.exit(0)

		time.sleep(1)
		nodes = devicenodes()
		devicedata(nodes)
		operate(nodes)

def start():
	thread = threading.Thread(target=main)
	thread.start()

def stop():
	global stopthread
	stopthread = True
	stopalldevicethread()

#########################