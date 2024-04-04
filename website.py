import threading
from flask import Flask, Response, render_template_string, jsonify, request, send_file, redirect, send_from_directory
from urllib.parse import unquote
import webcam
import os
import log
import json
from datetime import datetime
import subprocess
import time
from functools import wraps
import zipfile

#########################

sidebar = [
{"type": "btn", "name": "Devices", "url": "/devices"},
{"type": "btn", "name": "Captures", "url": "/captures"},
{"type": "btn", "name": "Logs", "url": "/logs"},
{"type": "btn", "name": "Settings", "url": "/settings"}
]

#########################

def sidebartxt(selectedbtn):
	global sidebar
	sidebarstr = ""
	for sidebarbtn in sidebar:
		if sidebarbtn["type"] == "btn":
			if selectedbtn.lower() == sidebarbtn["name"].lower():
				sidebarstr += f"<a href='{sidebarbtn['url']}' class='active'>{sidebarbtn['name']}</a>"
			else:
				sidebarstr += f"<a href='{sidebarbtn['url']}'>{sidebarbtn['name']}</a>"
		elif sidebarbtn["type"] == "bar":
			sidebarstr += "<center><div class='bar'></div></center>"
	return sidebarstr

def zipspecificdirectories(directories, output_zip_file):
	with zipfile.ZipFile(output_zip_file, "w", zipfile.ZIP_STORED) as zipf:
		for directory in directories:
			for root, _, files in os.walk(directory):
				zip_root = os.path.relpath(root, start=os.path.dirname(directory))
				for file in files:
					file_path = os.path.join(root, file)
					zip_path = os.path.join(zip_root, file)
					zipf.write(file_path, zip_path)

def checkpassword(f):
	@wraps(f)
	def decoratorcheckpassword(*args, **kwargs):
		password = request.cookies.get("password")
		if password == None:
			return redirect("/")
		password = unquote(password)
		if password != webcam.getsetting()["password"]:
			return redirect("/")
		return f(*args, **kwargs)
	return decoratorcheckpassword

def checkpasswordapi(f):
	@wraps(f)
	def decoratorcheckpasswordapi(*args, **kwargs):
		password = request.cookies.get("password")
		if password == None:
			return jsonify({"return": False, "error": "Incorrect or expired password.", "message": "🔒"})
		password = unquote(password)
		if password != webcam.getsetting()["password"]:
			return jsonify({"return": False, "error": "Incorrect or expired password.", "message": "🔒"})
		return f(*args, **kwargs)
	return decoratorcheckpasswordapi

#########################

def main():
	app.run(host="0.0.0.0", port=8080)

#########################

app = Flask(__name__)

#########################

@app.route('/')
def home():
	if request.cookies.get("password") == webcam.getsetting()["password"]:
		redirect = "<meta http-equiv='refresh' content='0; url=/devices'>"
	else:
		redirect = ""

	return render_template_string(open("./static/login.html", "r").read(),
		loggedin=redirect)

@app.route('/signin', methods=["POST"])
def signin():
	try:
		if request.get_json()["password"] == webcam.getsetting()["password"]:
			return jsonify({"return": True, "message": "✅", "correct": True})
		return jsonify({"return": True, "message": "❌", "correct": False})
	except Exception as e:
		return jsonify({"return": False, "error": e, "message": "❌", "correct": False})

@app.route('/devices')
@checkpassword
def devices():
	html = "<div class='box-visual-container'>"
	for device in os.listdir("./data/devices"):
		name, extension = os.path.splitext(device)

		status = "Active" if webcam.getdevicedata(name).get("active", False) else "Inactive"

		if status == "Active":
			info = "🟢 " + status
		else:
			info = "🔴 " + status

		url = f"/devices/{name}"

		box = f"""
			<div class="box-visual"><div class="box-visual-title">{webcam.getdevicedata(name).get("name", f"CRITICAL ERROR > {name}")}</div><div class="box-visual-content" style="justify-content: center;">
				<center>
					<p>{info}</p>
					<a href="{url}" id="bottom-left" style="text-decoration: none;">✏️</a>
				</center>
	    	</div></div>
		"""

		html += box

	html += "</div>"

	return render_template_string(open("./static/base.html", "r").read(),
		title="Panoptic",
		head="<link rel='stylesheet' href='/static/box.css'>",
		sidebar=sidebartxt("Devices"),
		body=html)

@app.route('/devices/<device>')
@checkpassword
def devicesany(device):
	device = unquote(device)
	devicedata = webcam.getdevicedata(device)

	nodeoptions = ", ".join([f'{{text: "{node}", value: "{node}"}}' for node in webcam.getdevicenodes(device)])

	html = f"""
	<script>
		function setdata() {{
		    
		    document.getElementById('displayname').value = '{devicedata.get("name", "")}';

		    document.getElementById('active').checked = {str(devicedata.get("active", False)).lower()};

		    document.getElementById('width').value = '{devicedata.get("width", "")}';
		    document.getElementById('height').value = '{devicedata.get("height", "")}';

		    document.getElementById('framerate').value = '{devicedata.get("framerate", "")}';

		    document.getElementById('recordinglength').value = '{devicedata.get("recordinglength", "")}';

		    document.getElementById('videonode').value = '{devicedata.get("videonode", None)}';
		    document.getElementById('audionode').value = '{devicedata.get("audionode", None)}';
		}}

		function setdatanodes(dropdownid) {{
			const options = [{nodeoptions}];

			const dropdown = document.getElementById(dropdownid);

			options.forEach(option => {{
				const addoption = document.createElement("option");
				addoption.text = option.text;
				addoption.value = option.value;
				dropdown.appendChild(addoption);
			}})
		}}

		document.addEventListener('DOMContentLoaded', function() {{
    		setdatanodes('videonode');
    		setdata();
		}});
	</script>
	"""

	boxes = [
		{"name": "Info", "content": f"Device<br>{device}<br><div class='setting-bar'></div>Device Name<br>{devicedata['name']}", "color": "purple"},

		{"name": "Name", "content": """
		Display Name
		<br>
		<input type='text' class='setting-input' id='displayname' placeholder='Hallway View'>
		""", "color": "yellow"},

		{"name": "Active", "content": "Enable/Disable<input type='checkbox' id='active' class='setting-checkbox' checked/>", "color": "green"},

		{"name": "Resolution", "content": """
		<span class="setting-label">Width x Height (PX)</span>
		<input type='text' id='width' class='setting-input' placeholder='480'>
		x
		<input type='text' id='height' class='setting-input' placeholder='360'><br>
		""", "color": "orange"},

		{"name": "Framerate", "content": """
		<span class="setting-label">Framerate (FPS)</span>
		<input type='text' id='framerate' class='setting-input' placeholder='30'>
		""", "color": "orange"},

		{"name": "Recording Length", "content": """
		<span class="setting-label">Recording Length (SEC)</span>
		<input type='text' id='recordinglength' class='setting-input' placeholder='600'>
		""", "color": "orange"},

		{"name": "Node", "content": f"""
		<span class="setting-label">Video Node</span>
		<select class='setting-select' id="videonode"> <option value="None" selected>None</option></select>

		<div class='setting-bar'></div>

		<span class="setting-label">Audio Node</span>
		<select class='setting-select' id="audionode"> <option value="None" selected>None</option> <option value="Default">Default</option> </select>
		""", "color": "blue"},

		{"name": "Save", "content": """
		<button class='setting-button-blue' id='save' onclick='saveButton()'>Save Settings</button>
		""", "color": "red"}
	]

	html += "<div class='box-side-container'>"
	for box in boxes:
		html += f"<div class='box-side-visual box-side-border-color-{box['color']}'><div class='box-side-visual-sidebar box-side-sidebar-color-{box['color']}'>"
		html += f"<div class='box-side-visual-title'>{box['name']}</div></div>"
		html += "<div class='box-side-visual-content'>"
		"""
		html += "<div class='settings-section'><div class='setting-item'>"
		<div class='setting-label'>Active</div>
		html += "<div class='setting-control'>"
		"""
		html += box['content']
		html += "</div></div>"

	html += "</div><div id='notification' class='notification'>"

	return render_template_string(open("./static/base.html", "r").read(),
		title="Panoptic",
		head="<link rel='stylesheet' href='/static/box.css'><link rel='stylesheet' href='/static/setting.css'><link rel='stylesheet' href='/static/notification.css'><script src='/static/savesetting.js'></script>",
		sidebar=sidebartxt("Devices"),
		body=html)

@app.route('/captures')
@checkpassword
def captures():
	days = []
	for device in os.listdir("./captures"):
		days.extend(os.listdir(f"./captures/{device}"))
	days = set(days)
	days = sorted(days, key=lambda date: datetime.strptime(date, "%Y-%m-%d"), reverse=True)

	html = "<div class='box-visual-container'>"
	for day in days:
		count = 0
		#gb = 0
		for device in os.listdir("./captures"):
			dayfolder = f"./captures/{device}/{day}"
			if os.path.isdir(dayfolder):
				for capture in os.listdir(dayfolder):
					count += 1
					#gb += os.path.getsize(os.path.join(dayfolder, capture))
		#gb = gb / (1 << 30)
		#Apparently getting the size is a very resource intensive task.

		#📊 {gb}GB<br>
		info = f"""📦 {count} Captures<br>💾 <a id='downloadLink{day}' href='#' style='color: black; display: inline-block; vertical-align: middle;' onclick="initdownload('/getcaptures/{day}', '{day}')">Download</a><span id='downloadProgress{day}' style='display: inline-block; vertical-align: middle;'></span>"""

		url = f"/captures/{day}"

		box = f"""
			<div class="box-visual"><div class="box-visual-title">{day}</div><div class="box-visual-content" style="justify-content: center;">
				<center>
					<p>{info}</p>
					<a href="{url}" id="bottom-left" style="text-decoration: none;">🎥</a>
				</center>
	    	</div></div>
		"""

		html += box

	html += "</div>"

	return render_template_string(open("./static/base.html", "r").read(),
		title="Panoptic",
		head="<link rel='stylesheet' href='/static/box.css'><script src='/static/downloadcaptures.js'></script><script src='/static/jszip.js'></script><script src='/static/filesaver.js'></script>",
		sidebar=sidebartxt("Captures"),
		body=html)

@app.route('/getcaptures/<day>')
@checkpassword
def getcaptures(day):
	captures = []
	for device in os.listdir("./captures"):
		if os.path.isdir(f"./captures/{device}/{day}"):
			for capture in os.listdir(f"./captures/{device}/{day}"):
				captures.append(f"/captures/{device}/{day}/{capture}")
	return jsonify(captures)

@app.route('/captures/<day>')
@checkpassword
def capturesany(day):
	captures = []
	for device in os.listdir("./captures"):
		name = webcam.getdevicedata(device)["name"]
		if os.path.isdir(f"./captures/{device}/{day}"):
			for capture in os.listdir(f"./captures/{device}/{day}"):
				captures.append({
						"filepath": f"./captures/{device}/{day}/{capture}",
						"urlpath": f"/captures/{device}/{day}/{capture}",
						"time": os.path.splitext(capture)[0],
						"device": device,
						"name": name
					})
	captures = sorted(captures, key=lambda x: datetime.strptime(x['time'], '%Y-%m-%d %H:%M:%S'), reverse=True)

	html = "<div class='box-visual-container'>"
	for capture in captures:
		box = f"""
			<div class="box-visual-under">
					<div class="box-visual-under-title">
						{capture['time']}
						<span class="toggle-info" style="float: right;">▼</span>
				        <div class="extra-info" style="display: none;">
				        	<div class='bar'></div>
				        	🆔 {capture['device']}
				        	<br>
				        	🎞️ {capture['name']}
				        	<br>
				            ⏱️ {capture['time']}
				        </div>
					</div><div class="box-visual-under-content" style="justify-content: center;">
				<center>
					<video width="100%" height="100%" controls style="object-fit: cover;">
						<source data-src="{capture['urlpath']}" type="video/mp4">
					</video>
				</center>
	    	</div></div>
		"""

		html += box

	html += "</div>"

	html += """
	<script>
		document.addEventListener('DOMContentLoaded', function () {
		    var toggleInfos = document.querySelectorAll('.toggle-info');
		    toggleInfos.forEach(function(toggleInfo) {
		        toggleInfo.addEventListener('click', function () {
		            var extraInfo = this.nextElementSibling;
		            if (extraInfo.style.display === 'none' || extraInfo.style.display === '') {
		                extraInfo.style.display = 'block';
		                this.textContent = '▲';
		            } else {
		                extraInfo.style.display = 'none';
		                this.textContent = '▼';
		            }
		        });
		    });

		    const observer = new IntersectionObserver((entries) => {
		        entries.forEach(entry => {
		            if (entry.isIntersecting) {
		                const video = entry.target.querySelector('video source');
		                if (video && video.dataset.src) {
		                    video.setAttribute('src', video.dataset.src);
		                    video.parentElement.load();
		                    observer.unobserve(entry.target);
		                }
		            }
		        });
		    }, {
		        rootMargin: '0px',
		        threshold: 0.1
		    });

		    document.querySelectorAll('.box-visual-under').forEach(box => {
		        observer.observe(box);
		    });
		});
	</script>

	<style>
		.toggle-info {
		  cursor: pointer;
		  transition: transform 0.3s ease;
		}

		.extra-info {
		  display: none;
		}

		.bar {
		  width: 100%;
		  height: 2px;
		  background-color: #241f31;
		  border-radius: 5px;
		  margin: 5px 0;
		}
	</style>
	"""

	return render_template_string(open("./static/base.html", "r").read(),
		title="Panoptic",
		head="<link rel='stylesheet' href='/static/box.css'>",
		sidebar=sidebartxt("Captures"),
		body=html)

@app.route('/captures/<device>/<day>/<capture>')
@checkpassword
def capturesreturn(device, day, capture):
	path = f"./captures/{unquote(device)}/{unquote(day)}/{unquote(capture)}"
	return send_file(path)

@app.route('/logs')
@checkpassword
def logs():
	with open("./data/log.txt", 'r') as file:
		lines = file.readlines()
	reversed_lines = lines[::-1]
	html_line = ''.join([line.strip() + '<br>' for line in reversed_lines])
	return render_template_string(open("./static/base.html", "r").read(),
		title="Panoptic",
		head="",
		sidebar=sidebartxt("Logs"),
		body=html_line)

@app.route('/settings')
@checkpassword
def settings():
	data = webcam.getsetting()

	html = f"""
	<script>
		function setdata() {{
			document.getElementById('disksize').value = '{data.get("disksize", "20")}';
		    document.getElementById('erasefrequency').value = '{data.get("erasefrequency", "24")}';
		    document.getElementById('password').value = '{data.get("password", "")}';
		}}

	    function setupSlider(sliderId, displayId) {{
	        var slider = document.getElementById(sliderId);
	        var display = document.getElementById(displayId);
	        display.innerHTML = slider.value;
	        slider.oninput = function() {{
	            display.innerHTML = this.value;
	        }}
	    }}

		document.addEventListener('DOMContentLoaded', function() {{
    		setdata();
    		setupSlider("erasefrequency", "erasefrequencynumb");
		}});
	</script>
	"""

	boxes = [
		{"name": "Disk", "content": """
		<span class="setting-label">Disk Size (GB)</span>
		<div class="settings-section">
			<input type='text' id='disksize' class='setting-input' placeholder='20'>
		</div>
		<div class='setting-explanation'>❔ The maxmimum allowed space for captures in gigabytes.</div>
		""", "color": "yellow"},

		{"name": "Erase", "content": """
		<span class="setting-label">Frequency (H)</span>
		<div class="settings-section">
			<div class="slider-wrapper">
				<div class="setting-item">
		  			<div class="setting-control">
		    			<input type="range" id="erasefrequency" name="erasefrequency" min="1" max="48" class="setting-slider">
		    			<span id="erasefrequencynumb" style="margin-left: 5px;">24</span>H
		  			</div>
				</div>
			</div>
		</div>
		<div class='setting-explanation'>❔ Frequency in hours at which files will be checked against disk size and deleted.</div>
		""", "color": "yellow"},

		{"name": "Password", "content": """
		<span class="setting-label">Password</span>
		<input type='text' id='password' class='setting-input' placeholder='panopticsystem'>
		<div class='setting-explanation'>❔ Password that is used when logging in. Session lasts 1 hour.</div>
		<div class='setting-bar'></div>
		<button class='setting-button-orange' id='logout' onclick='logoutButton()'>Logout</button>
		""", "color": "orange"},

		{"name": "Save", "content": """
		<button class='setting-button-blue' id='save' onclick='savesystemButton()'>Save Settings</button>
		""", "color": "red"},

		{"name": "Reboot", "content": """
		<button class='setting-button-red' id='reboot' onclick='rebootButton()'>Reboot Now</button>
		<div class='setting-explanation'>❔ When activated, the system will start a 5-second countdown to gracefully shutdown the devices before restarting.</div>
		""", "color": "red"}
	]

	html += "<div class='box-side-container'>"
	for box in boxes:
		html += f"<div class='box-side-visual box-side-border-color-{box['color']}'><div class='box-side-visual-sidebar box-side-sidebar-color-{box['color']}'>"
		html += f"<div class='box-side-visual-title'>{box['name']}</div></div>"
		html += "<div class='box-side-visual-content'>"
		html += box['content']
		html += "</div></div>"

	html += "</div><div id='notification' class='notification'></div>"

	return render_template_string(open("./static/base.html", "r").read(),
		title="Panoptic",
		head="<link rel='stylesheet' href='/static/box.css'><link rel='stylesheet' href='/static/setting.css'><link rel='stylesheet' href='/static/notification.css'><script src='/static/savesetting.js'></script>",
		sidebar=sidebartxt("Settings"),
		body=html)

#########################

@app.route('/savesetting/<device>', methods=['POST'])
@checkpasswordapi
def savesettingdevice(device):
	try:
		device = unquote(device)

		data = request.get_json()

		data["framerate"] = round(30 if int(data.get("framerate", 30)) < 1 else int(data.get("framerate", 30)))
		data["recordinglength"] = round(5 if int(data.get("recordinglength", 5)) < 5 else int(data.get("recordinglength", 5)))
		data["width"] = round(480 if int(data.get("width", 480)) < 120 else int(data.get("width", 480)))
		data["height"] = round(360 if int(data.get("height", 360)) < 90 else int(data.get("height", 360)))

		webcam.writedevicedata(device, data)
		print(log.l(f"SET: website.py > savesettingdevice > Updated {device} settings. Data: {data}"))
		return jsonify({"return": True, "message": "✅"})
	except Exception as e:
		return jsonify({"return": False, "error": e, "message": "❌"})

@app.route('/savesystemsetting', methods=['POST'])
@checkpasswordapi
def savesystemsetting():
	try:
		datawrite = request.get_json()

		datawrite["disksize"] = round(20 if int(datawrite.get("disksize", 0)) < 20 else int(datawrite.get("disksize", 20)))
		datawrite["erasefrequency"] = round(24 if int(datawrite.get("erasefrequency", 0)) < 1 else int(datawrite.get("erasefrequency", 24)))

		webcam.writesetting(datawrite)

		print(log.l(f"SET: website.py > savesystemsetting > Updated SYSTEM settings. Data: {datawrite}"))
		return jsonify({"return": True, "message": "✅"})
	except Exception as e:
		return jsonify({"return": False, "error": e, "message": "❌"})

@app.route('/reboot', methods=['PUT'])
@checkpasswordapi
def reboot():
	try:
		webcam.stopalldevicethread()
		threading.Thread(target=rebootcmd).start()
		return jsonify({"return": True, "message": "🔄"})
	except Exception as e:
		return jsonify({"return": False, "error": e, "message": "❌"})

def rebootcmd():
	time.sleep(5)
	subprocess.run("reboot")

@app.route('/savesetting', methods=['POST'])
@checkpasswordapi
def savesetting(device):
	try:
		data = request.get_json()
		print(log.l(f"SET: website.py > savesetting > Updated system settings. Data: {data}"))
		return jsonify({"return": True, "message": "✅"})
	except Exception as e:
		return jsonify({"return": False, "error": e, "message": "❌"})

@app.route('/download/captures/<day>', methods=['GET'])
@checkpasswordapi
def downloadcaptures(day):
	directories = []
	for device in os.listdir("./captures"):
		if os.path.exists(f"./captures/{device}/{day}"):
			directories.append(f"./captures/{device}/{day}")

	zipspecificdirectories(directories, "./data/captures.zip")
	return send_from_directory("./data", "captures.zip", as_attachment=True, download_name=f"panoptic-captures-{day}.zip", mimetype="application/zip")

#########################

def start():
	thread = threading.Thread(target=main)
	thread.start()

#########################