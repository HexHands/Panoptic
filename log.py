import os
from datetime import datetime

#########################

def l(data, time=True, file_path="./data/log.txt", max_size=1048576):
	data = str(data)

	if time:
		data = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " + data
	else:
		data = data

	with open(file_path, "a") as file:
		file.write(data + "\n")

	if os.path.getsize(file_path) > max_size:
		with open(file_path, "r") as file:
			lines = file.readlines()

		lines = lines[1:]

		with open(file_path, "w") as file:
			file.writelines(lines)

	return data

#########################