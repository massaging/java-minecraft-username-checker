minecraft username checker

a python tool that checks if minecraft java edition usernames are available using multiple api fallback systems. automatically handles rate limiting and includes a 4-letter username generator.

features

- checks username availability across 5 different apis for maximum reliability
- automatic fallback system (mojang api → minecraftuuid → playerdb → ashcon → minetools)
- rate limit detection with automatic pause and user prompts
- 4-letter username generator with two modes:
  - random 4l generator
  - repeater mode (generates usernames with 2 matching letters like "kkqw")
- saves all available usernames to a text file with namemc links
- color-coded output for easy reading
- real-time statistics tracking

how it works

the checker validates username format (3-16 characters, letters/numbers/underscores only) then queries multiple apis in sequence. if one api fails or gets rate limited, it automatically switches to the next backup api. when rate limits are detected, the program pauses and asks if you want to wait 3 minutes or continue anyway.

all available usernames are automatically saved to available_minecraft.txt with direct namemc profile links.

requirements

- python 3.6 or higher
- colorama library
- internet connection

installation

step 1: install python

if you dont have python installed:
- windows: download from python.org and install (make sure to check "add python to path")
- mac: download from python.org or use homebrew: brew install python
- linux: sudo apt install python3 python3-pip (ubuntu/debian) or sudo yum install python3 (fedora/rhel)

step 2: download this repository

click the green "code" button above and select "download zip", then extract it to a folder.

or use git:
git clone https://github.com/yourusername/java-minecraft-username-checker.git
cd java-minecraft-username-checker

step 3: install required library

open terminal or command prompt in the folder where you extracted the files, then run:

pip install colorama

or if that doesnt work try:

pip3 install colorama

or on windows:

python -m pip install colorama

note: the script will automatically try to install colorama if its missing, but its better to install it manually first.

step 4: run the script

python minecraft_checker.py

or if that doesnt work:

python3 minecraft_checker.py

usage

option 1: check single username
- enter one username at a time
- instant results with availability status

option 2: check from list
- paste multiple usernames (one per line)
- press enter twice when done
- set delay between checks (2-4 seconds recommended)

option 3: check from file
- create a .txt file with one username per line
- enter the filename when prompted
- set delay between checks

option 4: generate and check 4-letter usernames
- two generation modes:
  - random 4l: completely random 4-letter usernames
  - repeater: usernames with 2 matching letters (e.g., "kkqw", "oozq")
- three generation options:
  - generate specific amount
  - generate until available username found
  - generate continuously (ctrl+c to stop)

option 5: view statistics
- shows available, taken, errors, and success rate
- tracks how many times youve been rate limited

rate limiting

if you check too many usernames too quickly, apis will rate limit you (http 429 error). when this happens:
- the script automatically detects it
- pauses and prompts you to wait 3 minutes or continue
- switches to backup apis automatically
- tracks rate limit count in statistics

recommendation: use 2-4 second delays between checks to avoid rate limiting

output files

all available usernames are saved to available_minecraft.txt in this format:

username - https://namemc.com/profile/username

tips

- use longer delays (3-4 seconds) when checking large lists
- the 4l generator can run for hours - watch for rate limits
- repeater mode has slightly better chances of finding available names
- if rate limited, wait the full 3 minutes for best results
- close other programs using the same apis to reduce rate limiting

troubleshooting

"python is not recognized" error:
- you need to install python first (see step 1 above)
- make sure you checked "add python to path" during installation

"no module named colorama" error:
- run: pip install colorama
- the script should auto-install it but manual installation is more reliable

script closes immediately:
- open terminal/command prompt first
- navigate to the folder: cd path/to/folder
- then run: python minecraft_checker.py

notes

- checks minecraft java edition only (not bedrock)
- username format: 3-16 characters, letters/numbers/underscores
- multiple api system ensures high reliability even if one service is down
- all usernames are converted to lowercase for consistency

credits

massaging made this

license

free to use, modify, and distribute
