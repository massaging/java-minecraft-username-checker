# minecraft username checker

a multi-threaded username monitor that checks mojang + backup apis, supports proxies, and can send discord / telegram alerts when a name becomes available.

## requirements

- python 3.10+
- pip

## dependencies

installed automatically if missing:

- requests
- cloudscraper
- colorama

## setup

1. clone or download the project.
2. make sure these folders/files exist:
   data/
     usernames.txt
     proxies.txt
     available_minecraft.txt
   config.json
   checker.py

3. put the usernames you want to check in:
   data/usernames.txt
   one per line.

4. put proxies in:
   data/proxies.txt
   formats supported:
   ip:port
   ip:port:user:pass

5. edit config.json:
   {
     "threads": 20,
     "debug_mode": false,
     "enable_notifications": {
       "discord": false,
       "telegram": false
     },
     "discord_webhook": "",
     "telegram_bot_token": "",
     "telegram_chat_id": ""
   }

## installation

windows:
py -m pip install -r requirements.txt

linux / mac:
python3 -m pip install -r requirements.txt

you can create a requirements.txt:
requests
cloudscraper
colorama

## running

windows:
py checker.py

linux / mac:
python3 checker.py

when it starts:
- loads usernames
- loads proxies
- waits for you to press enter
- spins up threads
- checks mojang → ashcon backup
- logs available names to:
  data/available_minecraft.txt

## notifications

discord:
turn on in config.json:
"enable_notifications": { "discord": true }
set webhook:
"discord_webhook": ""

telegram:
"enable_notifications": { "telegram": true }
set bot token + chat id.

## features

- multithreaded checking
- proxy rotation
- backup validation api
- rps counter
- auto-save available names
- auto-skip already alerted usernames
- discord + telegram alerts
