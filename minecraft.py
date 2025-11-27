#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import time
import signal
import random
import threading
import string
import requests
from queue import Queue
from typing import List, Optional
from urllib.parse import quote
from datetime import datetime

try:
    import cloudscraper
except ImportError:
    print("[-] Installing cloudscraper...")
    os.system("pip install cloudscraper")
    import cloudscraper

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    print("[-] Installing colorama...")
    os.system("pip install colorama")
    from colorama import Fore, Style, init
    init(autoreset=True)

BANNER = f"""
{Fore.MAGENTA}   __  __  ___ ____    ____ _   _ _____ ____ _   _ ____  
{Fore.MAGENTA}  |  \/  |/ _ \___ \  / ___| | | | ____/ ___| | | |  _ \ 
{Fore.MAGENTA}  | |\/| | | | |__) | |   | | | |  _|| |   | | | | |_) |
{Fore.MAGENTA}  | |  | | |_| / __/  |___| |__| | |__| |___| |_| |  __/ 
{Fore.MAGENTA}  |_|  |_|\___/_____| \____|\____/|_____\____|\___/|_|    
{Fore.CYAN}               Minecraft Username Monitor v2025
{Fore.YELLOW}               Multi-threaded • Proxies • Notifications
{Style.RESET_ALL}"""

# Configurable Client-ID (public, safe)
MOJANG_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json"
}

class SentCache:
    def __init__(self, path="sent_minecraft.json"):
        self.path = path
        self.lock = threading.Lock()
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self.sent = set(json.load(f))
            except:
                self.sent = set()
        else:
            self.sent = set()

    def already_sent(self, username: str) -> bool:
        with self.lock:
            return username.lower() in self.sent

    def add(self, username: str):
        with self.lock:
            self.sent.add(username.lower())
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(list(self.sent), f, indent=2)


class Counters:
    def __init__(self):
        self.lock = threading.Lock()
        self.available = 0
        self.taken = 0
        self.errors = 0
        self.ratelimited = 0
        self.total_checked = 0
        self.rps = 0
        self.running = True


class Notifications:
    def __init__(self, cfg: dict, sent_cache: SentCache):
        n = cfg.get("enable_notifications", {})
        self.discord = str(n.get("discord", "false")).lower() == "true"
        self.telegram = str(n.get("telegram", "false")).lower() == "true"
        self.webhook = cfg.get("discord_webhook", "")
        self.bot_token = cfg.get("telegram_bot_token", "")
        self.chat_id = cfg.get("telegram_chat_id", "")
        self.sent_cache = sent_cache
        self.scraper = cloudscraper.create_scraper()

    def send(self, username: str):
        if self.sent_cache.already_sent(username):
            return

        link = f"https://namemc.com/profile/{username}"

        if self.discord and self.webhook:
            payload = {
                "embeds": [{
                    "title": f"Minecraft Username Dropping Soon!",
                    "description": f"**{username}** is available!\n[NameMC]({link})",
                    "color": 0x00ff00,
                    "timestamp": datetime.utcnow().isoformat(),
                    "footer": {"text": "Claim it before someone else!"}
                }]
            }
            try:
                self.scraper.post(self.webhook, json=payload, timeout=10)
            except: pass

        if self.telegram and self.bot_token and self.chat_id:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            text = f"MINECRAFT USERNAME AVAILABLE!\n\nUsername: `{username}`\nLink: {link}"
            try:
                self.scraper.get(url, params={"chat_id": self.chat_id, "text": text, "parse_mode": "Markdown"}, timeout=10)
            except: pass

        self.sent_cache.add(username)


class DataLoader:
    def __init__(self):
        os.makedirs("data", exist_ok=True)
        self.usernames_file = "data/usernames.txt"
        self.proxies_file = "data/proxies.txt"
        self.available_file = "data/available_minecraft.txt"
        self.lock = threading.Lock()

        for f in (self.usernames_file, self.proxies_file):
            if not os.path.exists(f):
                open(f, "w").close()
        if not os.path.exists(self.available_file):
            open(self.available_file, "w").close()

    def load_usernames(self) -> List[str]:
        try:
            with open(self.usernames_file, "r", encoding="utf-8") as f:
                return [line.strip() for line in f if line.strip() and self.validate(line.strip())]
        except:
            return []

    def validate(self, username: str) -> bool:
        return 3 <= len(username) <= 16 and all(c.isalnum() or c == '_' for c in username)

    def remove_username(self, username: str):
        with self.lock:
            try:
                lines = []
                with open(self.usernames_file, "r", encoding="utf-8") as f:
                    lines = [l.strip() for l in f if l.strip() != username]
                with open(self.usernames_file, "w", encoding="utf-8") as f:
                    f.write("\n".join(lines) + "\n")
            except: pass

    def save_available(self, username: str):
        with self.lock:
            with open(self.available_file, "a", encoding="utf-8") as f:
                f.write(f"{username} - https://namemc.com/profile/{username}\n")

    def load_proxies(self) -> List[Optional[str]]:
        try:
            with open(self.proxies_file, "r", encoding="utf-8") as f:
                lines = [l.strip() for l in f if l.strip()]
            proxies = []
            for line in lines:
                parts = line.split(":")
                if len(parts) == 2:
                    proxies.append(f"http://{parts[0]}:{parts[1]}")
                elif len(parts) == 4:
                    u, p = parts[2], quote(parts[3])
                    proxies.append(f"http://{u}:{p}@{parts[0]}:{parts[1]}")
            return proxies or [None]
        except:
            return [None]


class MinecraftChecker(threading.Thread):
    def __init__(self, queue: Queue, proxies, counters: Counters, notifier: Notifications, loader: DataLoader, debug: bool):
        super().__init__(daemon=True)
        self.q = queue
        self.proxies = proxies
        self.counters = counters
        self.notifier = notifier
        self.loader = loader
        self.debug = debug
        self.session = requests.Session()
        self.session.headers.update(MOJANG_HEADERS)

    def check(self, username: str) -> str:
        username = username.strip().lower()
        proxy = random.choice(self.proxies)
        proxies = {"http": proxy, "https": proxy} if proxy else None

        try:
            url = f"https://api.mojang.com/users/profiles/minecraft/{username}"
            r = self.session.get(url, proxies=proxies, timeout=10)

            if r.status_code == 200:
                return "taken"
            elif r.status_code == 204 or r.status_code == 404:
                # Double-check with NameMC or Ashcon to avoid false positives
                if self.backup_check(username, proxies):
                    return "taken"
                return "available"
            elif r.status_code == 429:
                time.sleep(2)
                return "ratelimit"
            else:
                return "error"
        except:
            return "error"

    def backup_check(self, username: str, proxies):
        try:
            r = requests.get(f"https://api.ashcon.app/mojang/v2/user/{username}", proxies=proxies, timeout=8)
            return r.status_code == 200
        except:
            return False

    def run(self):
        while self.counters.running:
            try:
                username = self.q.get(timeout=1)
            except:
                continue

            result = self.check(username)
            self.loader.remove_username(username)

            with self.counters.lock:
                self.counters.total_checked += 1
                if result == "available":
                    self.counters.available += 1
                    print(f"\r{Fore.GREEN}[+] AVAILABLE: {username}  → https://namemc.com/profile/{username}", flush=True)
                    self.loader.save_available(username)
                    self.notifier.send(username)
                elif result == "taken":
                    self.counters.taken += 1
                elif result == "ratelimit":
                    self.counters.ratelimited += 1
                    self.q.put(username)
                    time.sleep(1)
                else:
                    self.counters.errors += 1

            self.q.task_done()


def print_status(counters: Counters):
    while counters.running:
        with counters.lock:
            rps = counters.rps
            msg = f"Checked: {counters.total_checked} | +Avail: {counters.available} | Taken: {counters.taken} | RL: {counters.ratelimited} | Err: {counters.errors} | R/s: {rps}"
        print(f"\r{Fore.CYAN}[{msg.ljust(80)}]", end="", flush=True)
        time.sleep(0.2)


def calc_rps(counters: Counters):
    while counters.running:
        prev = counters.total_checked
        time.sleep(1)
        with counters.lock:
            counters.rps = counters.total_checked - prev


def stop(counters: Counters):
    counters.running = False
    print(f"\n{Fore.YELLOW}[!] Stopping threads...")


def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(BANNER)

    if not os.path.exists("config.json"):
        print(f"{Fore.RED}[!] config.json not found! Creating default...")
        default = {
            "threads": 20,
            "debug_mode": False,
            "enable_notifications": {
                "discord": False,
                "telegram": False
            },
            "discord_webhook": "",
            "telegram_bot_token": "",
            "telegram_chat_id": ""
        }
        with open("config.json", "w") as f:
            json.dump(default, f, indent=2)
        print(f"{Fore.YELLOW}[!] Edit config.json and restart.")
        return

    with open("config.json", "r") as f:
        cfg = json.load(f)

    loader = DataLoader()
    usernames = loader.load_usernames()
    if not usernames:
        print(f"{Fore.RED}No valid usernames in data/usernames.txt")
        return

    proxies = loader.load_proxies()
    threads = max(1, int(cfg.get("threads", 20)))
    debug = cfg.get("debug_mode", False)

    print(f"{Fore.CYAN}[*] Loaded {len(usernames)} usernames")
    print(f"{Fore.CYAN}[*] Using {len(proxies)} proxies | {threads} threads")
    print(f"{Fore.YELLOW}[!] Press ENTER to start...")
    input()

    q = Queue()
    for u in usernames:
        q.put(u)

    counters = Counters()
    notifier = Notifications(cfg, SentCache())
    workers = [MinecraftChecker(q, proxies, counters, notifier, loader, debug) for _ in range(threads)]

    for w in workers:
        w.start()

    threading.Thread(target=calc_rps, args=(counters,), daemon=True).start()
    threading.Thread(target=print_status, args=(counters,), daemon=True).start()
    signal.signal(signal.SIGINT, lambda s, f: stop(counters))

    try:
        q.join()
        time.sleep(2)
    except:
        pass
    finally:
        stop(counters)
        for w in workers:
            w.join(timeout=2)

        print(f"\n\n{Fore.CYAN}Final Results:")
        print(f"{Fore.GREEN}   Available : {counters.available}")
        print(f"{Fore.RED}   Taken     : {counters.taken}")
        print(f"{Fore.YELLOW}   Errors    : {counters.errors}")
        print(f"{Fore.WHITE}   Total     : {counters.total_checked}")
        if counters.available > 0:
            print(f"{Fore.GREEN}Check data/available_minecraft.txt")

if __name__ == "__main__":
    main()
