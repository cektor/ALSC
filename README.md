<a href="#">
    <img src="https://raw.githubusercontent.com/pedromxavier/flag-badges/main/badges/TR.svg" alt="made in TR">
</a>

# ALSC
This program was developed to facilitate maintenance and cleaning of Linux systems.

<h1 align="center">ALSC Logo</h1>

<p align="center">
  <img src="alsclo.png" alt="ALSC Logo" width="150" height="150">
</p>


----------------------

# Linux Screenshot
![Linux(pardus)](screenshot/alsc_linux.gif)  

--------------------
Install Git Clone and Python3

Github Package Must Be Installed On Your Device.

git
```bash
sudo apt install git -y
```

Python3
```bash
sudo apt install python3 -y 

```

pip
```bash
sudo apt install python3-pip

```

# Required Libraries

PyQt5
```bash
pip install PyQt5
```
PyQt5-sip
```bash
pip install PyQt5 PyQt5-sip
```

PyQt5-tools
```bash
pip install PyQt5-tools
```

Required Libraries for Debian/Ubuntu
```bash
sudo apt-get install python3-pyqt5
sudo apt-get install qttools5-dev-tools
```
psutil
```bash
pip3 install psutil
```

----------------------------------


# Installation
Install ALSC

```bash
sudo git clone https://github.com/cektor/ALSC.git
```
```bash
cd ALSC
```

```bash
python3 alsc.py

```

# To compile

NOTE: For Compilation Process pyinstaller must be installed. To Install If Not Installed.

pip install pyinstaller 

Linux Terminal 
```bash
pytohn3 -m pyinstaller --onefile --windowed alsc.py
```

MacOS VSCode Terminal 
```bash
pyinstaller --onefile --noconsole alsc.py
```

# To install directly on Linux





Linux (based debian) Terminal: Linux (debian based distributions) To install directly from Terminal.
```bash
wget -O Setup_Linux64.deb https://github.com/cektor/ALSC/releases/download/1.00/Setup_Linux64.deb && sudo apt install ./Setup_Linux64.deb && sudo apt-get install -f -y
```


Release Page: https://github.com/cektor/ALSC/releases/tag/1.00

----------------------------------
