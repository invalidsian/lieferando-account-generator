import colorama
import os
import asyncio
import requests
import json
import random
import re

from datetime import datetime
from webscout import tempid

colorama.init()

BLACK = colorama.Fore.BLACK
WHITE = colorama.Fore.WHITE
CYAN = colorama.Fore.LIGHTCYAN_EX

def get_current_time():
    return datetime.now().strftime('%H:%M:%S')

username = os.environ.get('USERNAME')

text = '''
                ██╗     ██╗███████╗███████╗███████╗██████╗  █████╗ ███╗   ██╗██████╗  ██████╗ 
                ██║     ██║██╔════╝██╔════╝██╔════╝██╔══██╗██╔══██╗████╗  ██║██╔══██╗██╔═══██╗
                ██║     ██║█████╗  █████╗  █████╗  ██████╔╝███████║██╔██╗ ██║██║  ██║██║   ██║
                ██║     ██║██╔══╝  ██╔══╝  ██╔══╝  ██╔══██╗██╔══██║██║╚██╗██║██║  ██║██║   ██║
                ███████╗██║███████╗██║     ███████╗██║  ██║██║  ██║██║ ╚████║██████╔╝╚██████╔╝
                ╚══════╝╚═╝╚══════╝╚═╝     ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═════╝  ╚═════╝ 
                        Account generator for lieferando.de - made by @invalidsian
'''

print(CYAN + text)

print(BLACK + f"[{get_current_time()}] " + CYAN + ">> " + WHITE + f"Hello {username}!")

try:
    num_accounts = int(input(BLACK + f"[{get_current_time()}] " + CYAN + ">> " + WHITE + "How many accounts would you like to generate? "))
    if num_accounts <= 0:
        print(BLACK + f"[{get_current_time()}] " + CYAN + ">> " + WHITE + "Invalid number entered. Exiting...")
        exit(1)
except ValueError:
    print(BLACK + f"[{get_current_time()}] " + CYAN + ">> " + WHITE + "Invalid number entered. Exiting...")
    exit(1)

random_password = ''.join(random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(12))

BASE_URL_SIGN_UP = "https://cw-api.takeaway.com/api/v34/user/sign_up"
BASE_URL_LOGIN = "https://cw-api.takeaway.com/api/v34/user/login"

with open("data/headers.json", "r") as file:
    headers = json.load(file)

def get_random_user_agent():
    with open("data/useragents.txt", "r") as file:
        user_agents = file.readlines()
    return random.choice(user_agents).strip()

headers["User-Agent"] = get_random_user_agent()
print(BLACK + f"[{get_current_time()}] " + CYAN + ">> " + WHITE + "Using User-Agent: " + headers["User-Agent"])

async def create_temp_mail_account(client):
    domains = await client.get_domains()
    if not domains:
        print(BLACK + f"[{get_current_time()}] " + CYAN + ">> " + WHITE + "No domains available. Please try again later.")
        return None, None

    email = await client.create_email(domain=domains[0].name)
    print(BLACK + f"[{get_current_time()}] " + CYAN + ">> " + WHITE + "Tempmail generated: " + email.email)
    print(BLACK + f"[{get_current_time()}] " + CYAN + ">> " + WHITE + "Token for accessing the email: " + email.token)
    return email.email, email.token

async def check_email_messages(client, email):
    while True:
        messages = await client.get_messages(email)
        if messages:
            print(BLACK + f"[{get_current_time()}] " + CYAN + ">> " + WHITE + "Checking for 2FA code...")
            return messages
        await asyncio.sleep(5)

def create_lieferando_account(email):
    while True:
        json_data = {
            'name': 'Alex',
            'email': email,
            'password': random_password,
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
    print(BLACK + f"[{get_current_time()}] " + CYAN + f">> " + WHITE + f"Generating {num_accounts} accounts...")

    email, token = await create_temp_mail_account(client)
    if not email:
        return

    headers["User-Agent"] = get_random_user_agent()
    print(BLACK + f"[{get_current_time()}] " + CYAN + ">> " + WHITE + "Using User-Agent: " + headers["User-Agent"])

    create_lieferando_account(email)

    messages = await check_email_messages(client, email)
    if messages:
        for message in messages:
            code = extract_2fa_code(message.body_text)
            if code:
                print(f"Your 2FA code: {code}")
                print(BLACK + f"[{get_current_time()}] " + CYAN + f">> " + WHITE + f"2FA code found: {code}")

                response_json = login_lieferando_account(email, random_password, code)

                save_account_data(email, random_password, response_json)
                
                print(BLACK + f"[{get_current_time()}] " + CYAN + f">> " + WHITE + f"Account {account_number}/{num_accounts} generated successfully!")
            else:
                print(BLACK + f"[{get_current_time()}] " + CYAN + f">> " + WHITE + f"No 2FA code found in email.")
                continue

async def main():
    client = tempid.Client()

    try:
        for i in range(1, num_accounts + 1):
            await generate_account(client, i)

    except Exception as e:
        print(BLACK + f"[{get_current_time()}] " + CYAN + f">> " + WHITE + f"An error occurred: {e}")

    finally:
        print(BLACK + f"[{get_current_time()}] " + CYAN + f">> " + WHITE + f"Join my discord server: https://discord.gg/RjX2CpdPpd")
        await client.close()

if __name__ == '__main__':
    asyncio.run(main())
