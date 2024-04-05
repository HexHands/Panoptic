![PanopticLogo](https://hexhands.github.io/HexHandsASSET/IMAGE/Panoptic/PanopticLogo.png)
# Panoptic
Panoptic is a security system that can be installed onto any Ubuntu computer. Being self-hosted, it allows you to gain independence from external dependencies. Panoptic offers a cost-effective and customizable alternative to subscription-based security camera systems. By leveraging your own hardware and managing the system directly, you eliminate ongoing fees and gain full control over your data privacy and storage solutions.

# Usage
Panoptic, designed for the Raspberry Pi 4 running Ubuntu, transforms any USB camera into a security camera. It includes a built-in website that offers a graphical interface to easily manage the system. Although specificlly design for the Raspberry Pi, Panoptic should be able to be run on any Ubuntu computer.

# Hardware
 - Raspberry Pi 4
 - 4 CPU
 - 8GB RAM
 - 20GB Disk Space
 - At least 1 Webcam

# Installation
    sudo apt update
    sudo apt install python3
    sudo apt install python3-pip
    pip install flask
    pip install gunicorn
    sudo apt-get install ffmpeg
    sudo apt-get install v4l-utils
    {may need more dependencies, let me know}
    
    cd {directory, where to install Ex: /home/user/Desktop/Panoptic}
    git clone https://github.com/HexHands/Panoptic.git

# Running
Once in the correct directory you may run the main.py script.

    python3 main.py

Or you may run it without cd-ing entering the directory. (enter your path to main.py, pwd command may help)

    python3 {directory path Ex:/home/user/Desktop/Panoptic}/main.py

# First Time Setup Guide
To start, after you've run the necessary commands and launched the main.py script in your command terminal or upon startup, head to the website it creates. You'll need to figure out the website's IP address, but remember, the port is always 8080. (type `ip a` in the command line to find the IP) The website URL will look something like `http://###.###.##.###:8080`. Once you get to the website, you'll see a screen like this.
![PanopticLogo](https://hexhands.github.io/HexHandsASSET/IMAGE/Panoptic/LoginPage.png)
For your first login, use the password `panopticsystem`. After logging in, you'll land on the devices section, which we'll set up soon. But first, head straight to settings to **change your password**. Just type a new password over the old one, hit save settings, and then log out.
![PanopticLogo](https://hexhands.github.io/HexHandsASSET/IMAGE/Panoptic/SettingsPageTutorial.png)
Next, go to the Devices section. Here, click on one of the little pencil icons to edit a device. (you might need to click through a few devices to find your camera)
![PanopticLogo](https://hexhands.github.io/HexHandsASSET/IMAGE/Panoptic/DevicesPageTutorial.png)
Then, you'll see your device's name, which is fetched from v4l2-ctl. In my case, I've selected something that's not a camera. For a camera, you'd update the display name, dimensions (width and height), framerate, recording length, video node, and audio node. You can also choose to enable or disable the camera. Make sure to save your settings.
![PanopticLogo](https://hexhands.github.io/HexHandsASSET/IMAGE/Panoptic/DevicesSettingPageTutorial.png)
Once a camera is enabled, it should start recording. You can verify this in the Logs section, where you'll want to see messages like "[...] has started recording..." If you encounter any errors from ffmpeg or similar issues, go back and adjust the device's node settings.
![PanopticLogo](https://hexhands.github.io/HexHandsASSET/IMAGE/Panoptic/LogsPage.png)
To view your recordings, head over to Captures. Here, each day's recordings are listed, and you can download a full day's worth as a zip file. To view individual recordings, click the little camera icon.
![PanopticLogo](https://hexhands.github.io/HexHandsASSET/IMAGE/Panoptic/CapturesPageTutorial.png)
On this page, you can watch each video. All the camera feeds are combined into a single stream, with the latest videos at the top. For more details on a video, click the dropdown arrow.
![PanopticLogo](https://hexhands.github.io/HexHandsASSET/IMAGE/Panoptic/CapturesDayPageTutorial.png)
Finally, the last two sections: Panoptic will take you to our website, and the GitHub button links to this repo! If you have any issues or questions, please contact me by submitting an issue on GitHub. And if you're really into it, you're welcome to contribute code!

# Disclaimer
This system isn't designed with high-level security for storing or accessing videos; it's intended for home use and is probably safer not connected to the internet. We can't promise it will work perfectly on all systems. If it does work for you, we're eager to hear about your experience. Please note, I am not responsible for any leaks or failures that may occur with the system.

# License
Creative Commons Attribution Non Commercial Share Alike 4.0 International (CC-BY-NC-SA-4.0).
http://creativecommons.org/licenses/by-nc-sa/4.0/
![CC BY-NC-SA](https://i.creativecommons.org/l/by-nc-sa/4.0/80x15.png)

# Credit
Panoptic repo contains 2 cached JavaScript libraries.
 - FileSaver (MIT License, *By* Eli Grey, [GitHub](https://github.com/eligrey/FileSaver.js/tree/master))
 - JSZip (MIT & GPL3 License, *By* Stuart Knightley, [GitHub](https://github.com/Stuk/jszip))

Panoptic depends on the following tools...
 - FFmpeg (GNU2.1 License, *By* FFmpeg Community, [GitHub](https://github.com/FFmpeg/FFmpeg), [Website](https://ffmpeg.org/))
 - Gunicorn (MIT License, *By* Benoit Chesneau, [GitHub](https://github.com/benoitc/gunicorn))
 - v4l-utils (LGPL License, *part of the* Video4Linux project, [LinuxTV](https://linuxtv.org))

Panoptic depends on the following Python library...
-   Flask (BSD License, *By* Armin Ronacher, [GitHub](https://github.com/pallets/flask))
