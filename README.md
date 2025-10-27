# minecraft username checker

> a python tool that checks if minecraft java edition usernames are available using multiple api fallback systems with automatic rate limit handling

![Python](https://img.shields.io/badge/python-3.6+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

---

## features

✓ checks username availability across 5 different apis for maximum reliability  
✓ automatic fallback system (mojang api → minecraftuuid → playerdb → ashcon → minetools)  
✓ rate limit detection with automatic pause and user prompts  
✓ 4-letter username generator with random and repeater modes  
✓ saves all available usernames to text file with namemc links  
✓ color-coded terminal output for easy reading  
✓ real-time statistics tracking  

---

## how it works

the checker validates username format (3-16 characters, letters/numbers/underscores only) then queries multiple apis in sequence. if one api fails or gets rate limited, it automatically switches to the next backup api. 

when rate limits are detected, the program pauses and asks if you want to wait 3 minutes or continue anyway.

all available usernames are automatically saved to `available_minecraft.txt` with direct namemc profile links.

---

## requirements

- python 3.6 or higher
- colorama library
- internet connection

---

## installation

### step 1: install python

**windows:**  
download from [python.org](https://www.python.org/downloads/) and install (make sure to check "add python to path")

**mac:**  
download from [python.org](https://www.python.org/downloads/) or use homebrew:
```bash
brew install python
```

**linux:**
```bash
# ubuntu/debian
sudo apt install python3 python3-pip

# fedora/rhel
sudo yum install python3
```

### step 2: download this repository

click the green "code" button above and select "download zip", then extract it to a folder.

or use git:
```bash
git clone https://github.com/yourusername/java-minecraft-username-checker.git
cd java-minecraft-username-checker
```

### step 3: install required library

open terminal or command prompt in the folder where you extracted the files, then run:
```bash
pip install colorama
```

if that doesn't work try:
```bash
pip3 install colorama
```

or on windows:
```bash
python -m pip install colorama
```

**note:** the script will automatically try to install colorama if it's missing, but manual installation is recommended.

### step 4: run the script
```bash
python minecraft_checker.py
```

or if that doesn't work:
```bash
python3 minecraft_checker.py
```

---

## usage guide

### option 1: check single username
enter one username at a time for instant availability results

### option 2: check from list
paste multiple usernames (one per line), press enter twice when done, then set delay between checks (2-4 seconds recommended)

### option 3: check from file
create a `.txt` file with one username per line, enter the filename when prompted, and set your delay

### option 4: generate & check 4-letter usernames

**two generation modes:**
- **random 4l:** completely random 4-letter usernames
- **repeater:** usernames with 2 matching letters (e.g., "kkqw", "oozq")

**three generation options:**
- generate specific amount
- generate until available username found
- generate continuously (ctrl+c to stop)

### option 5: view statistics
shows available, taken, errors, success rate, and rate limit count

---

## rate limiting

if you check too many usernames too quickly, apis will rate limit you (http 429 error). 

**when this happens:**
- the script automatically detects it
- pauses and prompts you to wait 3 minutes or continue
- switches to backup apis automatically
- tracks rate limit count in statistics

**recommendation:** use 2-4 second delays between checks to avoid rate limiting

---

## output files

all available usernames are saved to `available_minecraft.txt` in this format:
```
username - https://namemc.com/profile/username
```

---

## tips & tricks

💡 use longer delays (3-4 seconds) when checking large lists  
💡 the 4l generator can run for hours - watch for rate limits  
💡 repeater mode has slightly better chances of finding available names  
💡 if rate limited, wait the full 3 minutes for best results  
💡 close other programs using the same apis to reduce rate limiting  

---

## troubleshooting

**"python is not recognized" error:**
- you need to install python first (see installation step 1)
- make sure you checked "add python to path" during installation

**"no module named colorama" error:**
- run: `pip install colorama`
- the script should auto-install it but manual installation is more reliable

**script closes immediately:**
- open terminal/command prompt first
- navigate to the folder: `cd path/to/folder`
- then run: `python minecraft_checker.py`

---

## notes

📌 checks minecraft java edition only (not bedrock)  
📌 username format: 3-16 characters, letters/numbers/underscores  
📌 multiple api system ensures high reliability even if one service is down  
📌 all usernames are converted to lowercase for consistency  

---

## credits

**massaging made this**

---

## license

free to use, modify, and distribute

---

## support

found a bug? have a suggestion? open an issue or submit a pull request!

⭐ if you found this tool helpful, consider giving it a star!
