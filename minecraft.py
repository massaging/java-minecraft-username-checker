import requests
import time
import json
import sys
import os
import random
import string
from datetime import datetime

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    print("installing colorama...")
    os.system("pip install colorama")
    from colorama import Fore, Style, init
    init(autoreset=True)

class MinecraftUsernameChecker:
    def __init__(self):
        self.session = requests.Session()
        self.available = 0
        self.unavailable = 0
        self.errors = 0
        self.checked = 0
        self.checked_usernames = set()  # track checked usernames to avoid duplicates
        self.rate_limited = False  # track if we're currently rate limited
        self.rate_limit_count = 0  # count how many times we've been rate limited
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive'
        }
        
        self.session.headers.update(headers)
        
    def log_result(self, username, status, method="", details=""):
        # logs the result of a username check with timestamp and color coding
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if status == "available":
            self.available += 1
            color = Fore.GREEN
            symbol = "+"
        elif status == "taken":
            self.unavailable += 1
            color = Fore.RED
            symbol = "-"
        else:
            self.errors += 1
            color = Fore.YELLOW
            symbol = "!"
        
        self.checked += 1
        method_text = f" [{method.lower()}]" if method else ""
        details_text = f" - {details.lower()}" if details else ""
        print(f"{Fore.WHITE}[{timestamp}] {color}{symbol} {username.lower()}{method_text} - {status.lower()}{details_text}")
    
    def save_available(self, username):
        # saves available usernames to a text file with namemc link
        with open("available_minecraft.txt", "a", encoding="utf-8") as f:
            f.write(f"{username.lower()} - https://namemc.com/profile/{username.lower()}\n")
    
    def check_username_mojang_api(self, username):
        # checks username using mojang's official api (primary method)
        # returns dict with status: 'available', 'taken', or 'error'
        try:
            url = f"https://api.mojang.com/users/profiles/minecraft/{username}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'method': 'mojang api',
                    'status': 'taken',
                    'reason': 'active minecraft account found',
                    'user_info': {
                        'uuid': data.get('id'),
                        'name': data.get('name')
                    }
                }
            elif response.status_code == 204 or response.status_code == 404:
                # 204/404 means username doesn't exist = available
                return {
                    'method': 'mojang api',
                    'status': 'available',
                    'reason': 'username not found (available)'
                }
            elif response.status_code == 429:
                # 429 = rate limited, need to slow down
                self.rate_limited = True
                self.rate_limit_count += 1
                return {
                    'method': 'mojang api',
                    'status': 'error',
                    'reason': 'rate limited (429)'
                }
            else:
                return {
                    'method': 'mojang api',
                    'status': 'error',
                    'reason': f'api returned status code: {response.status_code}'
                }
                
        except Exception as e:
            return {
                'method': 'mojang api',
                'status': 'error',
                'reason': f'api error: {str(e)}'
            }
    
    def check_username_minecraftuuid(self, username):
        # checks username using minecraftuuid.com (backup method 1)
        # scrapes webpage to check if player profile exists
        try:
            url = f"https://minecraftuuid.com/player/{username}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                page_text = response.text.lower()
                
                # check if profile exists by looking for uuid data
                if "uuid" in page_text and "trimmed uuid" in page_text:
                    return {
                        'method': 'minecraftuuid',
                        'status': 'taken',
                        'reason': 'player profile found'
                    }
                elif "no user was found" in page_text or "player not found" in page_text:
                    return {
                        'method': 'minecraftuuid',
                        'status': 'available',
                        'reason': 'player not found'
                    }
                else:
                    # if page has substantial content, profile likely exists
                    if len(page_text) > 100:
                        return {
                            'method': 'minecraftuuid',
                            'status': 'taken',
                            'reason': 'profile data found'
                        }
                    else:
                        return {
                            'method': 'minecraftuuid',
                            'status': 'available',
                            'reason': 'minimal data returned'
                        }
            elif response.status_code == 404:
                return {
                    'method': 'minecraftuuid',
                    'status': 'available',
                    'reason': 'player not found (404)'
                }
            else:
                return {
                    'method': 'minecraftuuid',
                    'status': 'error',
                    'reason': f'returned status: {response.status_code}'
                }
                
        except Exception as e:
            return {
                'method': 'minecraftuuid',
                'status': 'error',
                'reason': f'error: {str(e)}'
            }
    
    def check_username_playerdb(self, username):
        # checks username using playerdb api (backup method 2)
        # queries their database for player information
        try:
            url = f"https://playerdb.co/api/player/minecraft/{username}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                # check if api call was successful and returned player data
                if data.get('success') and data.get('data'):
                    player_data = data['data']['player']
                    return {
                        'method': 'playerdb',
                        'status': 'taken',
                        'reason': 'player found in database',
                        'user_info': {
                            'uuid': player_data.get('id'),
                            'username': player_data.get('username')
                        }
                    }
                else:
                    return {
                        'method': 'playerdb',
                        'status': 'available',
                        'reason': 'player not found in database'
                    }
            elif response.status_code == 404:
                return {
                    'method': 'playerdb',
                    'status': 'available',
                    'reason': 'player not found (404)'
                }
            else:
                return {
                    'method': 'playerdb',
                    'status': 'error',
                    'reason': f'playerdb returned status: {response.status_code}'
                }
                
        except Exception as e:
            return {
                'method': 'playerdb',
                'status': 'error',
                'reason': f'playerdb error: {str(e)}'
            }
    
    def check_username_ashcon(self, username):
        # checks username using ashcon api (backup method 3)
        # third-party api that checks mojang's database
        try:
            url = f"https://api.ashcon.app/mojang/v2/user/{username}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'method': 'ashcon',
                    'status': 'taken',
                    'reason': 'account found',
                    'user_info': {
                        'uuid': data.get('uuid'),
                        'username': data.get('username')
                    }
                }
            elif response.status_code == 404:
                return {
                    'method': 'ashcon',
                    'status': 'available',
                    'reason': 'username not found (404)'
                }
            else:
                return {
                    'method': 'ashcon',
                    'status': 'error',
                    'reason': f'ashcon returned status: {response.status_code}'
                }
                
        except Exception as e:
            return {
                'method': 'ashcon',
                'status': 'error',
                'reason': f'ashcon error: {str(e)}'
            }
    
    def check_username_minetools(self, username):
        # checks username using minetools api (backup method 4)
        # checks for uuid in their database
        try:
            url = f"https://api.minetools.eu/uuid/{username}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                # if uuid exists in response, account is taken
                if data.get('id'):
                    return {
                        'method': 'minetools',
                        'status': 'taken',
                        'reason': 'uuid found',
                        'user_info': {
                            'uuid': data.get('id'),
                            'username': data.get('name')
                        }
                    }
                else:
                    return {
                        'method': 'minetools',
                        'status': 'available',
                        'reason': 'no uuid found'
                    }
            elif response.status_code == 404:
                return {
                    'method': 'minetools',
                    'status': 'available',
                    'reason': 'player not found (404)'
                }
            else:
                return {
                    'method': 'minetools',
                    'status': 'error',
                    'reason': f'returned status: {response.status_code}'
                }
                
        except Exception as e:
            return {
                'method': 'minetools',
                'status': 'error',
                'reason': f'error: {str(e)}'
            }
    
    def validate_username(self, username):
        # validates minecraft username format rules
        # must be 3-16 chars, only letters/numbers/underscores
        if len(username) < 3 or len(username) > 16:
            return False, "username must be 3-16 characters"
        if not all(c.isalnum() or c == '_' for c in username):
            return False, "username can only contain letters, numbers, and underscores"
        return True, ""
    
    def handle_rate_limit(self):
        # handles rate limiting by pausing and asking user to continue
        # gives option to wait or continue (not recommended)
        print(f"\n{Fore.RED}rate limit detected!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}you've been rate limited by the api. this happens when checking too fast.{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}recommended: wait a few minutes before continuing{Style.RESET_ALL}\n")
        
        choice = input(f"{Fore.WHITE}[1] wait 3 minutes\n[2] continue anyway (not recommended)\n{Fore.YELLOW}select option (1-2): {Style.RESET_ALL}").strip()
        
        if choice == '1':
            print(f"{Fore.CYAN}waiting 3 minutes...{Style.RESET_ALL}")
            for i in range(180, 0, -30):
                print(f"{Fore.WHITE}{i} seconds remaining...{Style.RESET_ALL}")
                time.sleep(30)
            print(f"{Fore.GREEN}resuming checks...{Style.RESET_ALL}\n")
            self.rate_limited = False
        else:
            print(f"{Fore.YELLOW}continuing without waiting (may result in more errors)...{Style.RESET_ALL}\n")
            self.rate_limited = False
    
    def check_username(self, username):
        # main function to check if a minecraft username is available
        # tries multiple apis in order until getting a definitive answer
        username = username.strip()
        
        # validate username format first
        valid, error_msg = self.validate_username(username)
        if not valid:
            self.log_result(username, "error", "validation", error_msg)
            return {
                'method': 'validation',
                'status': 'error',
                'reason': error_msg
            }
        
        # if we hit rate limit earlier, prompt user
        if self.rate_limited:
            self.handle_rate_limit()
        
        # try methods in order with delays between apis
        methods = [
            ('mojang api', self.check_username_mojang_api),
            ('minecraftuuid', self.check_username_minecraftuuid),
            ('playerdb', self.check_username_playerdb),
            ('ashcon', self.check_username_ashcon),
            ('minetools', self.check_username_minetools)
        ]
        
        result = None
        for i, (name, method) in enumerate(methods):
            result = method(username)
            
            # check if we got rate limited
            if '429' in result.get('reason', '') or 'rate limit' in result.get('reason', '').lower():
                self.rate_limited = True
                self.rate_limit_count += 1
                if not hasattr(self, '_rate_limit_warned'):
                    print(f"{Fore.YELLOW}rate limit detected, switching to backup apis...{Style.RESET_ALL}")
                    self._rate_limit_warned = True
            
            # if we got a definitive answer (available or taken), use it
            if result['status'] in ['available', 'taken']:
                break
            
            # if error and not the last method, try next method
            if result['status'] == 'error' and i < len(methods) - 1:
                if not hasattr(self, '_fallback_warned'):
                    print(f"{Fore.YELLOW}primary method failed, trying backup apis...{Style.RESET_ALL}")
                    self._fallback_warned = True
                time.sleep(1)  # small delay between api calls
                continue
        
        # log the result with color coding and details
        if result['status'] == 'available':
            self.log_result(username, "available", result['method'])
            self.save_available(username)
        elif result['status'] == 'taken':
            details = ""
            if result.get('user_info'):
                info = result['user_info']
                parts = []
                if info.get('uuid'):
                    parts.append(f"uuid: {info['uuid'][:8]}...")
                if info.get('username'):
                    parts.append(f"name: {info['username']}")
                details = " | ".join(parts)
            elif result.get('reason'):
                details = result['reason']
            
            self.log_result(username, "taken", result['method'], details)
        else:
            self.log_result(username, "error", result['method'], result.get('reason', ''))
        
        return result
    
    def generate_4l_username(self):
        # generates a unique random 4-letter username
        # ensures no duplicates are checked twice
        while True:
            username = ''.join(random.choices(string.ascii_lowercase, k=4))
            if username not in self.checked_usernames:
                self.checked_usernames.add(username)
                return username
    
    def generate_4l_repeater(self):
        # generates a unique random 4-letter username with 2 repeating letters
        # pattern: 2 same letters + 2 different letters (e.g., kkqw, oozq)
        while True:
            # pick 2 letters: one will repeat, one will be unique
            letters = random.sample(string.ascii_lowercase, 2)
            repeating_letter = letters[0]
            other_letter1 = letters[1]
            other_letter2 = random.choice(string.ascii_lowercase)
            
            # create pattern: 2 same letters + 2 different letters
            username_list = [repeating_letter, repeating_letter, other_letter1, other_letter2]
            random.shuffle(username_list)
            username = ''.join(username_list)
            
            # make sure it actually has exactly 2 of one letter (is a valid repeater)
            letter_counts = {}
            for char in username:
                letter_counts[char] = letter_counts.get(char, 0) + 1
            
            has_pair = any(count == 2 for count in letter_counts.values())
            
            if has_pair and username not in self.checked_usernames:
                self.checked_usernames.add(username)
                return username
    
    def generate_and_check_4l(self, count=None, delay=2, stop_on_available=False, repeater_mode=False):
        # generates and checks 4-letter usernames in real-time
        # can run specific count, until available found, or continuously
        mode_text = "4-letter repeater" if repeater_mode else "4-letter"
        print(f"\n{Fore.CYAN}starting {mode_text} username generator...{Style.RESET_ALL}")
        if repeater_mode:
            print(f"{Fore.MAGENTA}repeater mode: generates usernames with 2 repeating letters (e.g., kkqw, oozq){Style.RESET_ALL}")
        
        if count:
            print(f"{Fore.CYAN}will generate and check {count} usernames{Style.RESET_ALL}")
        else:
            print(f"{Fore.CYAN}generating until stopped (ctrl+c to stop){Style.RESET_ALL}")
        
        if stop_on_available:
            print(f"{Fore.GREEN}will stop when an available username is found{Style.RESET_ALL}")
        
        print(f"{Fore.YELLOW}delay between checks: {delay} seconds{Style.RESET_ALL}\n")
        
        checked_count = 0
        try:
            while True:
                if count and checked_count >= count:
                    break
                
                # generate username based on mode
                if repeater_mode:
                    username = self.generate_4l_repeater()
                else:
                    username = self.generate_4l_username()
                    
                result = self.check_username(username)
                checked_count += 1
                
                # stop if we found an available username and stop_on_available is true
                if stop_on_available and result['status'] == 'available':
                    print(f"\n{Fore.GREEN}found available username! stopping...{Style.RESET_ALL}\n")
                    break
                
                if count is None or checked_count < count:
                    time.sleep(delay)
                    
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}4l generation stopped by user.{Style.RESET_ALL}")
        
        return checked_count
    
    def check_multiple_usernames(self, usernames, delay=2):
        # checks multiple usernames with delay between requests
        # automatically handles rate limiting
        rate_limited = False
        
        for i, username in enumerate(usernames):
            result = self.check_username(username)
            
            # check if we got rate limited
            if result.get('reason') and '429' in result.get('reason', ''):
                rate_limited = True
                if not hasattr(self, '_rate_limit_warned'):
                    print(f"{Fore.YELLOW}rate limited - automatically switching to backup methods{Style.RESET_ALL}")
                    self._rate_limit_warned = True
            
            if i < len(usernames) - 1:
                current_delay = delay
                if rate_limited:
                    current_delay = delay + 2  # add extra delay if rate limited
                time.sleep(current_delay)
        
        return self.get_results()
    
    def get_results(self):
        # returns summary of all checks performed
        return {
            'available': self.available,
            'unavailable': self.unavailable,
            'errors': self.errors,
            'total': self.checked
        }
    
    def print_stats(self):
        # prints colored statistics summary
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.WHITE}statistics:")
        print(f"{Fore.GREEN}+ available: {self.available}")
        print(f"{Fore.RED}- taken: {self.unavailable}")
        print(f"{Fore.YELLOW}! errors: {self.errors}")
        print(f"{Fore.WHITE}total checked: {self.checked}")
        if self.rate_limit_count > 0:
            print(f"{Fore.YELLOW}times rate limited: {self.rate_limit_count}")
        if self.checked > 0:
            success_rate = ((self.available + self.unavailable) / self.checked * 100)
            print(f"success rate: {success_rate:.1f}%")
        print(f"{Fore.CYAN}{'='*60}\n")


def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # massive banner that can't be changed
    banner = f"""{Fore.MAGENTA}
    
    ███╗   ███╗ █████╗ ███████╗███████╗ █████╗  ██████╗ ██╗███╗   ██╗ ██████╗ 
    ████╗ ████║██╔══██╗██╔════╝██╔════╝██╔══██╗██╔════╝ ██║████╗  ██║██╔════╝ 
    ██╔████╔██║███████║███████╗███████╗███████║██║  ███╗██║██╔██╗ ██║██║  ███╗
    ██║╚██╔╝██║██╔══██║╚════██║╚════██║██╔══██║██║   ██║██║██║╚██╗██║██║   ██║
    ██║ ╚═╝ ██║██║  ██║███████║███████║██║  ██║╚██████╔╝██║██║ ╚████║╚██████╔╝
    ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝╚═╝  ╚═══╝ ╚═════╝ 
                                                                                
    ███╗   ███╗ █████╗ ██████╗ ███████╗    ████████╗██╗  ██╗██╗███████╗       
    ████╗ ████║██╔══██╗██╔══██╗██╔════╝    ╚══██╔══╝██║  ██║██║██╔════╝       
    ██╔████╔██║███████║██║  ██║█████╗         ██║   ███████║██║███████╗       
    ██║╚██╔╝██║██╔══██║██║  ██║██╔══╝         ██║   ██╔══██║██║╚════██║       
    ██║ ╚═╝ ██║██║  ██║██████╔╝███████╗       ██║   ██║  ██║██║███████║       
    ╚═╝     ╚═╝╚═╝  ╚═╝╚═════╝ ╚══════╝       ╚═╝   ╚═╝  ╚═╝╚═╝╚══════╝       
                                                                                
    {Style.RESET_ALL}"""
    
    print(banner)
    
    checker = MinecraftUsernameChecker()
    
    try:
        while True:
            print(f"\n{Fore.CYAN}options:")
            print(f"{Fore.WHITE}[1] check single username")
            print(f"{Fore.WHITE}[2] check from list (paste usernames)")
            print(f"{Fore.WHITE}[3] check usernames from file")
            print(f"{Fore.WHITE}[4] generate & check 4-letter usernames")
            print(f"{Fore.WHITE}[5] view statistics")
            print(f"{Fore.WHITE}[6] exit")
            
            choice = input(f"\n{Fore.YELLOW}select option (1-6): {Style.RESET_ALL}").strip()
            
            if choice == '1':
                username = input(f"{Fore.YELLOW}enter username: {Style.RESET_ALL}").strip()
                if username:
                    print(f"\n{Fore.CYAN}checking minecraft username...{Style.RESET_ALL}\n")
                    checker.check_username(username)
                    checker.print_stats()
            
            elif choice == '2':
                print(f"{Fore.YELLOW}enter usernames (one per line, press enter twice when done):{Style.RESET_ALL}")
                usernames = []
                while True:
                    username = input().strip()
                    if not username:
                        break
                    usernames.append(username)
                
                if not usernames:
                    print(f"{Fore.RED}no usernames entered{Style.RESET_ALL}")
                    continue
                
                delay = float(input(f"{Fore.YELLOW}delay between checks (recommend 2-4 seconds): {Style.RESET_ALL}").strip() or "2")
                
                print(f"\n{Fore.CYAN}checking {len(usernames)} usernames...{Style.RESET_ALL}\n")
                checker.check_multiple_usernames(usernames, delay)
                checker.print_stats()
                
                if checker.available > 0:
                    print(f"{Fore.GREEN}{checker.available} available username(s) saved to available_minecraft.txt{Style.RESET_ALL}")
            
            elif choice == '3':
                filename = input(f"{Fore.YELLOW}enter filename (txt file with one username per line): {Style.RESET_ALL}").strip()
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        usernames = [line.strip() for line in f if line.strip()]
                    
                    if usernames:
                        print(f"\n{Fore.GREEN}found {len(usernames)} usernames in file.{Style.RESET_ALL}")
                        
                        delay = float(input(f"{Fore.YELLOW}delay between checks (recommend 2-4 seconds): {Style.RESET_ALL}").strip() or "2")
                        
                        print(f"\n{Fore.CYAN}checking {len(usernames)} usernames from file...{Style.RESET_ALL}\n")
                        checker.check_multiple_usernames(usernames, delay)
                        checker.print_stats()
                        
                        if checker.available > 0:
                            print(f"{Fore.GREEN}{checker.available} available username(s) saved to available_minecraft.txt{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}no usernames found in file.{Style.RESET_ALL}")
                        
                except FileNotFoundError:
                    print(f"{Fore.RED}file not found.{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.RED}error reading file: {e}{Style.RESET_ALL}")
            
            elif choice == '4':
                print(f"\n{Fore.CYAN}4-letter username generator{Style.RESET_ALL}")
                print(f"{Fore.WHITE}[1] generate random 4l usernames")
                print(f"{Fore.WHITE}[2] generate 4l repeaters (2 matching letters)")
                
                mode_choice = input(f"\n{Fore.YELLOW}select mode (1-2): {Style.RESET_ALL}").strip()
                
                if mode_choice not in ['1', '2']:
                    print(f"{Fore.RED}invalid option{Style.RESET_ALL}")
                    continue
                
                repeater_mode = (mode_choice == '2')
                
                print(f"\n{Fore.CYAN}generation options{Style.RESET_ALL}")
                print(f"{Fore.WHITE}[1] generate specific amount")
                print(f"{Fore.WHITE}[2] generate until available found")
                print(f"{Fore.WHITE}[3] generate continuously (ctrl+c to stop)")
                
                gen_choice = input(f"\n{Fore.YELLOW}select option (1-3): {Style.RESET_ALL}").strip()
                
                delay = float(input(f"{Fore.YELLOW}delay between checks (recommend 2-4 seconds): {Style.RESET_ALL}").strip() or "2")
                
                if gen_choice == '1':
                    count = int(input(f"{Fore.YELLOW}how many to generate: {Style.RESET_ALL}").strip())
                    checker.generate_and_check_4l(count=count, delay=delay, repeater_mode=repeater_mode)
                    checker.print_stats()
                    
                elif gen_choice == '2':
                    checker.generate_and_check_4l(delay=delay, stop_on_available=True, repeater_mode=repeater_mode)
                    checker.print_stats()
                    
                elif gen_choice == '3':
                    checker.generate_and_check_4l(delay=delay, repeater_mode=repeater_mode)
                    checker.print_stats()
                    
                else:
                    print(f"{Fore.RED}invalid option{Style.RESET_ALL}")
                
                if checker.available > 0:
                    print(f"{Fore.GREEN}{checker.available} available username(s) saved to available_minecraft.txt{Style.RESET_ALL}")
            
            elif choice == '5':
                checker.print_stats()
            
            elif choice == '6':
                print(f"\n{Fore.CYAN}goodbye{Style.RESET_ALL}")
                break
            
            else:
                print(f"{Fore.RED}invalid option{Style.RESET_ALL}")
                
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}program interrupted by user.{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}an error occurred: {e}{Style.RESET_ALL}")
    
    input(f"\n{Fore.WHITE}press enter to exit...{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
