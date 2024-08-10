# Lieferando.de Account Generator

This Python script automates the creation of user accounts for the website lieferando.de. It was developed by me @invalidsian and utilizes temporary email addresses for registration and handling Two-Factor Authentication (2FA).

## Prerequisites

Ensure that all necessary Python packages are installed. You can find the dependencies in the `requirements.txt` file. Install them with the following command:

```bash
pip install -r requirements.txt
```

### Libraries Used
- `colorama`: For coloring terminal output.
- `requests`: For sending HTTP requests to the lieferando.de API.
- `asyncio`: For asynchronous task execution.
- `json`: For processing JSON data.
- `random`: For generating random values, e.g., passwords.
- `re`: For extracting 2FA codes from email content.
- `datetime`: For retrieving the current time.
- `os`: For accessing environment variables.

## How It Works

The script performs the following steps:

1. **Load Username**: The username is fetched from the environment variables.
2. **Account Generation Count**: The user is prompted to enter the number of accounts to generate.
3. **Create Temporary Email Address**: A temporary email address with a token for later use is generated.
4. **Create Account on lieferando.de**: A new account on lieferando.de is created using the generated email address.
5. **Verify 2FA Code**: The script monitors the emails and extracts the 2FA code when it becomes available.
6. **Login and Save Account Data**: The account is logged into on lieferando.de, and the account data is saved to a file.

## Usage

1. Ensure the `headers.json` file with the required header data is available in the `data` directory.
2. Ensure the `useragents.txt` file with a list of User-Agent strings is available in the `data` directory.
3. Run the script:
   
   ```bash
   python main.py
   ```
4. Follow the instructions in the terminal.

## Troubleshooting

- **Rate Limiting**: If you receive a rate-limiting message from Cloudflare, the script will automatically use a new User-Agent and retry.
- **No Available Domains**: If no temporary email domains are available, try again later.

## Disclaimer

This script was created for educational purposes only. The author takes no responsibility for the use of this script in any way that violates the terms of service of lieferando.de or applicable laws.

## Contact

For questions visit my [discord server](https://discord.gg/RjX2CpdPpd)!
