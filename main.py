import os
import asyncio
import string

try:
    import colorama
    import requests
    from pystyle import Center
    from webscout import tempid
except ModuleNotFoundError:
    os.system("pip install colorama")
    os.system("pip install requests")
    os.system("pip install webscout")

import json
import random
import re
from datetime import datetime

colorama.init()

BLACK = colorama.Fore.BLACK
WHITE = colorama.Fore.WHITE
ORANGE = "\033[38;2;255;165;0m"
RESET = colorama.Style.RESET_ALL

ASCII = r"""
    {o}
    __    __________________________  ___    _   ______  ____ 
   / /   /  _/ ____/ ____/ ____/ __ \/   |  / | / / __ \/ __ \
  / /    / // __/ / /_  / __/ / /_/ / /| | /  |/ / / / / / / /
 / /____/ // /___/ __/ / /___/ _, _/ ___ |/ /|  / /_/ / /_/ / 
/_____/___/_____/_/   /_____/_/ |_/_/  |_/_/ |_/_____/\____/{r}"""

CREDITS = r"""
{o}|{r} Made by: {o}invalidsian
{o}|{r} UI developed by: {o}vjpe.py
"""

def get_current_time():
    return datetime.now().strftime('%H:%M:%S')

username = os.environ.get('USERNAME')

text = Center.XCenter(ASCII.replace('{o}', ORANGE).replace('{r}', RESET))
cred = Center.XCenter(CREDITS.replace('{o}', ORANGE).replace('{r}', RESET))

print(text)
print(cred)

print(BLACK + f"[{get_current_time()}] " + ORANGE + ">> " + WHITE + f"Hello {username}!")

try:
    num_accounts = int(input(BLACK + f"[{get_current_time()}] " + ORANGE + ">> " + WHITE + "How many accounts would you like to generate? "))
    if num_accounts <= 0:
        print(BLACK + f"[{get_current_time()}] " + ORANGE + ">> " + WHITE + "Invalid number entered. Exiting...")
        exit(1)
except ValueError:
    print(BLACK + f"[{get_current_time()}] " + ORANGE + ">> " + WHITE + "Invalid number entered. Exiting...")
    exit(1)

BASE_URL_SIGN_UP = "https://cw-api.takeaway.com/api/v34/user/sign_up"
BASE_URL_LOGIN = "https://cw-api.takeaway.com/api/v34/user/login"

with open("data/headers.json", "r") as file:
    headers = json.load(file)

def get_random_user_agent():
    with open("data/useragents.txt", "r") as file:
        user_agents = file.readlines()
    return random.choice(user_agents).strip()

headers["User-Agent"] = get_random_user_agent()
print(BLACK + f"[{get_current_time()}] " + ORANGE + ">> " + WHITE + "Using User-Agent: " + headers["User-Agent"])

def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def get_random_username():
    with open("data/usernames.txt", "r") as file:
        usernames = file.readlines()
    return random.choice(usernames).strip()

async def create_temp_mail_account(client):
    domains = await client.get_domains()
    if not domains:
        print(BLACK + f"[{get_current_time()}] " + ORANGE + ">> " + WHITE + "No domains available. Please try again later.")
        return None, None

    email = await client.create_email(domain=domains[0].name)
    print(BLACK + f"[{get_current_time()}] " + ORANGE + ">> " + WHITE + "Tempmail generated: " + email.email)
    print(BLACK + f"[{get_current_time()}] " + ORANGE + ">> " + WHITE + "Token for accessing the email: " + email.token)
    return email.email, email.token

async def check_email_messages(client, email):
    while True:
        messages = await client.get_messages(email)
        if messages:
            print(BLACK + f"[{get_current_time()}] " + ORANGE + ">> " + WHITE + "Checking for 2FA code...")
            return messages
        await asyncio.sleep(5)

def create_lieferando_account(email, name, password):
    while True:
        json_data = {
            'name': name,
            'email': email,
            'password': password,
            'newsletter': False,
        }
        response = requests.post(BASE_URL_SIGN_UP, headers=headers, json=json_data)
        if "cloudflare" in response.text:
            print("Rate limited or something... retrying...")
            headers["User-Agent"] = get_random_user_agent()
            continue
        else:
            print(response.text)
            break

def extract_2fa_code(email_body):
    matches = re.findall(r'\b[A-Za-z0-9]{6}\b', email_body)
    for match in matches:
        if match.lower() not in ["import", "family", "roboto", "normal", "weight", "assets", "format"]:
            return match
    return None

def login_lieferando_account(email, password, code):
    json_data = {
        'username': email,
        'password': password,
        'twoFactorAuthenticationCode': code,
    }
    response = requests.post(BASE_URL_LOGIN, headers=headers, json=json_data)
    return response.json()

def save_account_data(email, password, response_json):
    with open("data/accounts.txt", "a") as file:
        file.write(f"{email}:{password} | {response_json}\n")

async def generate_account(client, account_number):
    print(BLACK + f"[{get_current_time()}] " + ORANGE + f">> " + WHITE + f"Generating {num_accounts} accounts...")

    email, token = await create_temp_mail_account(client)
    if not email:
        return

    username = get_random_username()
    password = generate_random_password()

    headers["User-Agent"] = get_random_user_agent()
    print(BLACK + f"[{get_current_time()}] " + ORANGE + ">> " + WHITE + "Using User-Agent: " + headers["User-Agent"])

    create_lieferando_account(email, username, password)

    messages = await check_email_messages(client, email)
    if messages:
        for message in messages:
            code = extract_2fa_code(message.body_text)
            if code:
                print(f"Your 2FA code: {code}")
                print(BLACK + f"[{get_current_time()}] " + ORANGE + f">> " + WHITE + f"2FA code found: {code}")

                response_json = login_lieferando_account(email, password, code)

                save_account_data(email, password, response_json)
                
                print(BLACK + f"[{get_current_time()}] " + ORANGE + f">> " + WHITE + f"Account {account_number}/{num_accounts} generated successfully!")
            else:
                print(BLACK + f"[{get_current_time()}] " + ORANGE + f">> " + WHITE + f"No 2FA code found in email.")
                continue

async def main():
    client = tempid.Client()

    try:
        for i in range(1, num_accounts + 1):
            await generate_account(client, i)

    except Exception as e:
        print(BLACK + f"[{get_current_time()}] " + ORANGE + f">> " + WHITE + f"An error occurred: {e}")

    finally:
        print(BLACK + f"[{get_current_time()}] " + ORANGE + f">> " + WHITE + f"Join my discord server: https://discord.gg/RjX2CpdPpd")
        await client.close()

if __name__ == '__main__':
    asyncio.run(main())
