# minecraft username checker

a multithreaded python tool for checking minecraft username availability using mojang + ashcon backup apis, optional proxies, and discord / telegram notifications.

## install

1. install python 3.10+
2. download or clone this repo
3. install dependencies:
   pip install -r requirements.txt

## requirements.txt

requests  
cloudscraper  
colorama  

## project layout

data/
  usernames.txt  
  proxies.txt  
  available_minecraft.txt  

checker.py  
config.json  
readme.md  
.gitignore  

## setup

### usernames  
edit:
data/usernames.txt  
add usernames one per line.

### proxies  
edit:
data/proxies.txt  
supported formats:
ip:port  
ip:port:user:pass  

### config  
edit:
config.json  
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

## .gitignore (what it does)

.gitignore tells git which files to ignore so they don’t upload to github.  
this keeps your repo clean and prevents leaking things like proxies or cached data.

current .gitignore:
__pycache__/  
*.pyc  
sent_minecraft.json  
data/available_minecraft.txt  

## running

windows:
py checker.py

linux/mac:
python3 checker.py

## behavior

- loads usernames  
- loads proxies  
- waits for enter  
- starts multi-thread checking  
- verifies via mojang + ashcon backup  
- saves available names to:
  data/available_minecraft.txt  

terminal shows:
checked total  
available found  
taken  
errors  
ratelimits  
requests per second  

## notifications

discord:
enable:
"enable_notifications": { "discord": true }
set:
"discord_webhook": "your webhook"

telegram:
enable:
"enable_notifications": { "telegram": true }
set bot token + chat id.

## features

- multithreaded checking  
- proxy rotation  
- backup validation api  
- rps counter  
- auto-save available names  
- skip already-notified names  
- discord + telegram alerts  
