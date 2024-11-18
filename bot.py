import asyncio
import aiohttp
import random
import json
from faker import Faker
from fake_useragent import UserAgent
import urllib.parse
from typing import List, Optional
import os
from urllib.parse import urlparse, parse_qs
from colorama import init, Fore, Back, Style
import time
from datetime import datetime

init(autoreset=True)
def display_header():
    print(f"""
==================================================================
{Fore.CYAN + Style.BRIGHT}

 █████╗ ██╗██████╗ ██████╗ ██████╗  ██████╗ ██████╗ 
██╔══██╗██║██╔══██╗██╔══██╗██╔══██╗██╔═══██╗██╔══██╗
███████║██║██████╔╝██║  ██║██████╔╝██║   ██║██████╔╝
██╔══██║██║██╔══██╗██║  ██║██╔══██╗██║   ██║██╔═══╝ 
██║  ██║██║██║  ██║██████╔╝██║  ██║╚██████╔╝██║     
╚═╝  ╚═╝╚═╝╚═╝  ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝     
                                                    
██╗███╗   ██╗███████╗██╗██████╗ ███████╗██████╗     
██║████╗  ██║██╔════╝██║██╔══██╗██╔════╝██╔══██╗    
██║██╔██╗ ██║███████╗██║██║  ██║█████╗  ██████╔╝    
██║██║╚██╗██║╚════██║██║██║  ██║██╔══╝  ██╔══██╗    
██║██║ ╚████║███████║██║██████╔╝███████╗██║  ██║    
╚═╝╚═╝  ╚═══╝╚══════╝╚═╝╚═════╝ ╚══════╝╚═╝  ╚═╝    

Join our Telegram channel for the latest updates: t.me/airdropinsiderid

BLOCKMESH AUTO REFERRAL BOT - Airdrop Insider{Style.RESET_ALL}
==================================================================
    """)

def log_info(message: str):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{Fore.WHITE}[{Fore.CYAN}{timestamp}{Fore.WHITE}] {Fore.GREEN}INFO {Fore.WHITE}→ {message}")

def log_success(message: str):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{Fore.WHITE}[{Fore.CYAN}{timestamp}{Fore.WHITE}] {Fore.GREEN}SUCCESS {Fore.WHITE}→ {message}")

def log_error(message: str):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{Fore.WHITE}[{Fore.CYAN}{timestamp}{Fore.WHITE}] {Fore.RED}ERROR {Fore.WHITE}→ {message}")

def log_warning(message: str):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{Fore.WHITE}[{Fore.CYAN}{timestamp}{Fore.WHITE}] {Fore.YELLOW}WARNING {Fore.WHITE}→ {message}")

class TempMailAPI:
    def __init__(self, api_key: str = ''):
        self.api_key = api_key
        self.base_url = 'https://api.tempmail.lol'

    async def create_inbox(self) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/generate") as response:
                data = await response.json()
                return {
                    'address': data['address'],
                    'token': data['token']
                }

    async def check_inbox(self, token: str) -> List[dict]:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/auth/{token}") as response:
                data = await response.json()
                return data.get('email', [])

class RegistrationBot:
    def __init__(self):
        self.API_KEY = ''
        self.fake = Faker()
        self.ua = UserAgent()
        self.temp_mail = TempMailAPI(self.API_KEY)

    def load_proxies(self) -> List[str]:
        try:
            with open('proxies.txt', 'r') as f:
                proxies = [line.strip() for line in f if line.strip()]
                if not proxies:
                    log_warning("Proxy file is empty or not found. Continuing without proxy.")
                return proxies
        except Exception as e:
            log_warning(f"Error reading proxies.txt: {e}. Continuing without proxy.")
            return []

    async def get_ip_address(self, session, proxy=None):
        try:
            async with session.get('https://api.ipify.org?format=json', proxy=proxy) as response:
                data = await response.json()
                return data['ip']
        except Exception as e:
            return "Unable to fetch IP"

    def get_random_proxy(self, proxies: List[str]) -> Optional[str]:
        return random.choice(proxies) if proxies else None

    @staticmethod
    def extract_ref_code_from_url(url: str) -> str:
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        ref_code = params.get('invite_code', [None])[0]
        if not ref_code:
            log_error("No invite_code found in the URL.")
            exit(1)
        return ref_code

    @staticmethod
    def extract_confirmation_link(aws_tracking_link: str) -> str:
        decoded_link = urllib.parse.unquote(
            aws_tracking_link.split("L0/")[1].split("/1/")[0]
        )
        return decoded_link

    async def check_inbox_with_retry(self, token: str, max_retries: int = 10) -> List[dict]:
        for retry in range(max_retries):
            try:
                emails = await self.temp_mail.check_inbox(token)
                if emails:
                    log_success("Emails found in inbox")
                    return emails
                log_info(f"Waiting for confirmation email... ")
                await asyncio.sleep(5)
            except Exception as e:
                log_error(f"Error checking inbox: {e}")
                await asyncio.sleep(5)
        log_error("Max retries reached. No emails found.")
        return []

    def save_credentials(self, email: str, password: str, token: str, confirmation_link: str, ip_address: str):
        credentials = (
            f"Email: {email}\n"
            f"Password: {password}\n"
            f"Temporary Email Token: {token}\n"
            f"Confirmation Link: {confirmation_link}\n"
            f"IP Address: {ip_address}\n"
            f"{'-' * 50}\n\n"
        )
        try:
            with open('accounts.txt', 'a') as f:
                f.write(credentials)
            log_success(f"Credentials saved to accounts.txt")
        except Exception as e:
            log_error(f"Error saving credentials: {e}")

    async def create_and_register(self, refcode: str, registration_number: int):
        try:
            log_info(f"Starting registration #{registration_number}")
            
            proxies = self.load_proxies()
            proxy = self.get_random_proxy(proxies)
            
            async with aiohttp.ClientSession() as session:
                if proxy:
                    log_info(f"Using proxy: {Fore.CYAN}{proxy}")
                    ip_address = await self.get_ip_address(session, proxy)
                    log_info(f"Using IP address: {Fore.CYAN}{ip_address}")
                else:
                    log_info("No proxy used")
                    ip_address = await self.get_ip_address(session)
                    log_info(f"Using IP address: {Fore.CYAN}{ip_address}")

                inbox = await self.temp_mail.create_inbox()
                
                rand_pass = self.fake.password()
                
                log_success(f"Credentials generated:")
                print(f"{Fore.WHITE}Email: {Fore.CYAN}{inbox['address']}")
                print(f"{Fore.WHITE}Password: {Fore.CYAN}{rand_pass}")
                
                log_info(f"Temporary Email Token: {Fore.GREEN}{inbox['token']}")
                log_info(f"Registering, please wait...")

                registration_data = {
                    'email': inbox['address'],
                    'password': rand_pass,
                    'password_confirm': rand_pass,
                    'invite_code': refcode
                }

                headers = {
                    "User-Agent": self.ua.random,
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "*/*",
                    "Origin": "https://app.blockmesh.xyz",
                    "Referer": "https://app.blockmesh.xyz/ext/register"
                }

                async with session.post(
                    "https://app.blockmesh.xyz/register_api",
                    data=registration_data,
                    headers=headers,
                    proxy=proxy
                ) as response:
                    response_text = await response.text()
                    
                    if response.status == 200:
                        log_success(f"Registration successful!")
                        confirmation_link = await self.handle_email_confirmation(session, inbox, proxy)
                        self.save_credentials(
                            inbox['address'],
                            rand_pass,
                            inbox['token'],
                            confirmation_link if confirmation_link else "Not found",
                            ip_address
                        )
                    elif response.status == 400:
                        try:
                            error_data = json.loads(response_text)
                            error_message = error_data.get('message', 'Unknown error')
                            log_error(f"Registration failed: {error_message}")
                        except json.JSONDecodeError:
                            log_error(f"Registration failed with status 400: {response_text}")
                        return
                    else:
                        log_error(f"Unexpected response status: {response.status}")
                        log_error(f"Response body: {response_text}")
                        return

        except Exception as e:
            log_error(f"An error occurred: {e}")
            return 

    async def handle_email_confirmation(self, session, inbox, proxy):
        try:
            emails = await self.check_inbox_with_retry(inbox['token'])
            
            if not emails:
                log_error("No emails received or inbox expired")
                return None

            log_info(f"Found {len(emails)} email(s) in inbox")

            for email in emails:
                log_info(f"Checking email: {email['subject']}")
                
                if "Confirmation" in email['subject'] or "confirm" in email['html']:
                    log_success("Found confirmation email")
                    
                    import re
                    aws_link_match = re.search(
                        r'https://[a-z0-9.-]+\.awstrack\.me[^\s]+',
                        email['html']
                    )
                    
                    if aws_link_match:
                        aws_tracking_link = aws_link_match.group(0)
                        log_info(f"Found confirmation link: {Fore.CYAN}{aws_tracking_link}")

                        confirmation_link = self.extract_confirmation_link(aws_tracking_link)
                        log_info("Verifying Account...")

                        async with session.get(confirmation_link, proxy=proxy) as conf_response:
                            if conf_response.status == 200:
                                log_success("Email confirmed successfully")
                                return confirmation_link
                            else:
                                log_error(f"Email confirmation failed: {conf_response.status}")
                                return None

                        break
                    else:
                        log_error("No confirmation link found in email")
                        return None

        except Exception as e:
            log_error(f"Error during email confirmation: {e}")
            return None

async def main():
    display_header()
    bot = RegistrationBot()
    
    print(f"{Fore.YELLOW}Welcome :) Please Enter Your Details{Style.RESET_ALL}")
    ref_url = input(f"{Fore.GREEN}Input referral link{Fore.WHITE}: ")
    ref_code = bot.extract_ref_code_from_url(ref_url)
    
    num_registrations = int(input(f"{Fore.GREEN}Enter number of referrals{Fore.WHITE}: "))
    print(f"{Fore.CYAN}{'─' * 50}\n")
    
    successful_registrations = 0
    failed_registrations = 0
    start_time = time.time()
    
    log_info(f"Starting {num_registrations} registrations with referral code: {Fore.YELLOW}{ref_code}")
    
    for i in range(num_registrations):
        print(f"\n{Fore.CYAN}{'═' * 70}")
        log_info(f"Processing registration {i + 1}/{num_registrations}")
        print(f"{Fore.CYAN}{'═' * 70}")
        try:
            await bot.create_and_register(ref_code, i + 1)
            successful_registrations += 1
        except Exception as e:
            failed_registrations += 1
            log_error(f"Registration failed: {str(e)}")
        
        if i < num_registrations - 1:
            await asyncio.sleep(1)

    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\n{Fore.CYAN}{'═' * 70}")
    print(f"{Fore.YELLOW}Registration Summary:{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'─' * 50}")
    print(f"{Fore.WHITE}Total Attempted: {Fore.CYAN}{num_registrations}")
    print(f"{Fore.WHITE}Successful: {Fore.GREEN}{successful_registrations}")
    print(f"{Fore.WHITE}Failed: {Fore.RED}{failed_registrations}")
    print(f"{Fore.WHITE}Success Rate: {Fore.YELLOW}{(successful_registrations/num_registrations*100):.1f}%")
    print(f"{Fore.WHITE}Total Duration: {Fore.YELLOW}{duration:.1f} seconds")
    print(f"{Fore.WHITE}Average Time per Registration: {Fore.YELLOW}{(duration/num_registrations):.1f} seconds")
    print(f"{Fore.CYAN}{'─' * 50}")
    if successful_registrations > 0:
        print(f"{Fore.GREEN}Successfully saved {successful_registrations} accounts to accounts.txt")
    print(f"{Fore.CYAN}{'═' * 70}\n")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log_warning("Script terminated by user")
        exit(0)