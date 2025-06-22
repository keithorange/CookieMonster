Certainly! Here’s your **README** updated with the new "How to use" section explaining how to start the system with **start.py** and how to get fresh cookies saved as files, plus some extra explanation to clarify the new file-based architecture - all while keeping your original style and tone intact:

---

# 🍪👹 Cloudflare Cookie Monster - THE UNSTOPPABLE COOKIE STEALER FOR PRO CODERS

---

## What the hell is this?

You want **infinite, fresh, legit cookies** from ANY Cloudflare-protected website without solving captchas or getting blocked? This is your **nuclear-grade weapon**.

Forget shitty scrapers and flaky bypasses. This tool:

- **Spins up multiple stealth browsers** that act like real humans behind Cloudflare.
- Each browser runs on a unique local port as a **cookie proxy**.
- You hit these proxies with requests, and they spit out **fresh AF cookies and user agents**.
- Browsers auto-restart on your schedule to stay **undetectable & fresh**.
- No weird database pools or connection bullshit. Just reliable, simple Python subprocesses.
- Runs clean, stable, no freezes, no crashes.

---

## Why does this matter? Why is this badass?

Cloudflare is like a digital fortress, stopping lazy scrapers, bots, haters. But **you’re better**. This tool takes you inside, no questions asked:

- **Unlimited Cookies:** Get as many fresh, valid cookies as you want. Rotate 'em, scale 'em.
- **Works everywhere:** APIs, dashboards, login pages - doesn’t matter. If Cloudflare’s in front, this tool slices right through.
- **Massive parallelism:** Run 20 stealth browsers at once. Scale up cookie harvesting like a boss.
- **No risk of freezing:** Other tools choke under load or DB locks. Not this one. It’s rock solid.
- **Easy to automate:** The cookie proxies speak HTTP. Plug ‘em in your scripts, bots, or whatever you hack on.
- **Minimal footprint:** Lightweight, portable, works on your laptop, server, wherever.

---

## How does it work *really*?

1. **Launch stealth browsers** (`cookie_proxy_fetcher.py`) on localhost ports. Each looks like a legit user.
2. **Manage those browsers** from a central Python script - kill, restart, track ports - now using files instead of a database.
3. **Send URL requests to these local proxies**. They handle Cloudflare, get you real cookies.
4. **Grab cookies and user agents from response headers** - DONE.
5. **They restart themselves after a while** to avoid stale cookies or bans.
6. No external DB nonsense - all tracking of cookies and ports is done via simple JSON files.
7. Each cookie is saved as a separate `.json` file in a managed directory for easy access and editing.

---

## What can YOU do with this?

- Take **control of 99.9% Cloudflare-protected sites**.
- **Impersonate real users** with valid cookies - no captcha, no roadblocks.
- **Steal session tokens** for pentesting, scraping, or automation.
- Collect data behind Cloudflare’s iron curtain at scale.
- Build crazy resilient scraping infrastructure.
- Automate form fills, content grabs, API calls with legit sessions.

---

## How to get started in 4 steps - no excuses

```bash
git clone https://github.com/your-repo/cloudflare-cookie-monster.git
cd cloudflare-cookie-monster
pip install -r requirements.txt
```

### Step 1 - Start Stealth Browsers (Cookie Proxies):

Run the manager script (called **start.py**) to launch multiple stealth browser instances on your machine:

```bash
python3 start.py --num_parallel 5 --base_port 8010
```

This will:

- Launch 5 stealth browser proxies on ports 8010 to 8014.
- Save active port info in `~/browser_ports.json`.
- Manage lifecycle of each browser, auto-restarting them on schedule.
- Log colorful status messages with cookie 🍪 and monster emojis.

### Step 2 - Get Fresh Cookies in Your Script:

Use the cookie manager's method to fetch cookies **saved as JSON files** inside a directory named `.cloudflare_cookies_{name}/` within the project. Each cookie is stored individually.

Example using Python's cookie manager API (from `cookie_manager.py`):

```python
import asyncio
from cookie_manager import get_fresh_cookie_with_retries

async def main():
    def your_generate_request():
        # Return target URL and params for cookie fetching
        return "https://example.com", {"param1": "value1"}
    
    # Replace 'default' with your manager name if needed
    cookies, cookie_id = await get_fresh_cookie_with_retries("default", your_generate_request, verbose=True)
    
    print("🍪 Fresh cookie data:", cookies)
    print("🆔 Cookie file ID:", cookie_id)

asyncio.run(main())
```

- The cookie manager reads/writes cookies as JSON files, one cookie per file.
- Cookies are automatically refreshed and expired cookies cleaned in the background.
- Use the cookie data and user agent in your scraping requests to appear legit.

### Step 3 - Use the cookie proxies directly (optional):

You can also call the cookie proxies (running on ports started before) directly via HTTP:

```python
import requests

port = 8010
url = "https://some-cloudflare-protected-site.com/api/data"

response = requests.post(f"http://localhost:{port}/raw_html_file", json={"file_path": "/tmp/myurls.txt"})

cookies = response.headers.get("cookies")
ua = response.headers.get("user_agent")

print("🔥 Fresh cookies:", cookies)
print("🕵️‍♂️ User Agent:", ua)
```

### Step 4 - Cleaning up:

To kill all running proxies and clear saved ports:

```bash
python3 start.py --kill
```

---

## Pro Tips for Hackers

- Keep `--num_parallel` below 20 unless you want your machine to melt.
- Adjust `--first_browser_age` and `--kill_spacing_s` to fine-tune auto-restart intervals.
- Use a load balancer or rotate ports so requests spread evenly.
- Modify or inspect individual cookie JSON files anytime in `.cloudflare_cookies_{name}` directory.
- No GUI needed; runs clean in terminal with colorful logs and hacker emojis 🍪👹🕵️‍♂️

---

## Bottom line: Why it beats everything else

| Other scrapers               | Cloudflare Cookie Monster                   |
|-----------------------------|---------------------------------------------|
| Freeze under load            | Handles parallel stealth browsers perfectly|
| Get blocked after 1 request  | Auto-restart browsers for fresh valid cookies|
| Fragile DB pools & locks     | Simple file + subprocess management          |
| Need manual Captcha solving  | Fully automated Cloudflare bypass             |
| Single cookie/session only   | Infinite cookies across many ports           |

---

## Licensing and Ethics

⚠️ This tool is *powerful and dangerous*. Use it for **testing, research, or authorized operations only**. Respect privacy & laws.

---

## Summary

You want **unlimited, fresh, legit Cloudflare cookies**?  
You want **a powerful, reliable tool that never freezes, never crashes**?  
You want **to run dozens of stealth browsers and grab cookies for anything**?

**This is your weapon. Run it. Own Cloudflare.**

🍪👹🕵️‍♂️

---

# Ready to hack the impossible? Start now.

