import json
import re
import os
from urllib.parse import urlparse

from cloudflare_bypasser_functions import CloudflareBypasser
from DrissionPage import ChromiumPage, ChromiumOptions
from fastapi import FastAPI, HTTPException, Response, Request
from pydantic import BaseModel
from typing import Dict
import argparse

import uvicorn
import atexit

from DrissionPage.common import Settings

import asyncio
import os
import logging
from typing import Dict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Settings.set_singleton_tab_obj(False)



CONFIG = {
    "HEADLESS": True,
    "SERVER_PORT": 8010,
    "NUM_TABS": 1,
    "MAX_CONNECTIONS": 100000000,
    "BROWSER_PATH": "/usr/bin/google-chrome",
    "DOCKER_MODE": os.getenv("DOCKERMODE", "false").lower() == "true",
    "LOGGING": False,
    "CHROME_ARGUMENTS": [
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-extensions",
        "--disable-software-rasterizer",
        "--disable-dev-shm-usage",
        "--disable-setuid-sandbox",
        "--no-zygote",
        "--disable-accelerated-2d-canvas",
        "--disable-gpu-rasterization",
        "--disable-infobars",
        "--disable-notifications",
        "--mute-audio",
        "--no-default-browser-check",
        "--no-first-run",
        "--disable-background-networking",
        "--disable-background-timer-throttling",
        "--disable-client-side-phishing-detection",
        "--disable-default-apps",
        "--disable-hang-monitor",
        "--disable-popup-blocking",
        "--disable-prompt-on-repost",
        "--disable-sync",
        "--disable-translate",
        "--metrics-recording-only",
        "--safebrowsing-disable-auto-update",
        "--password-store=basic",
        "--use-mock-keychain",
        "--disable-features=TranslateUI,BlinkGenPropertyTrees",
        "--enable-features=NetworkService,NetworkServiceInProcess",
        "--force-color-profile=srgb",
        "--disable-backgrounding-occluded-windows",
        "--disable-component-extensions-with-background-pages",
        "--disable-ipc-flooding-protection",
    ]
}


app = FastAPI()

# Global browser instance and display
browser_instance = None
display = None
tab_ids = []
tab_in_use = {}  # Track which tabs are currently in use
current_tab_index = 0

# Semaphore to limit concurrent connections
connection_semaphore = None

# Function to get the next available tab
def get_next_tab():
    global tab_ids, current_tab_index, tab_in_use
    
    # Try to find an unused tab
    for i in range(len(tab_ids)):
        idx = (current_tab_index + i) % len(tab_ids)
        if not tab_in_use.get(tab_ids[idx], False):
            tab_in_use[tab_ids[idx]] = True
            current_tab_index = (idx + 1) % len(tab_ids)
            return tab_ids[idx]
    
    # If all tabs are in use, create a new tab
    new_tab = browser_instance.new_tab()
    tab_ids.append(new_tab)
    tab_in_use[new_tab] = True
    return new_tab

# Function to release a tab
def release_tab(tab_id):
    global tab_in_use
    if tab_id in tab_in_use:
        tab_in_use[tab_id] = False

# Pydantic model for the response
class CookieResponse(BaseModel):
    cookies: Dict[str, str]
    user_agent: str

# Function to check if the URL is safe
def is_safe_url(url: str) -> bool:
    parsed_url = urlparse(url)
    ip_pattern = re.compile(
        r"^(127\.0\.0\.1|localhost|0\.0\.0\.0|::1|10\.\d+\.\d+\.\d+|172\.1[6-9]\.\d+\.\d+|172\.2[0-9]\.\d+\.\d+|172\.3[0-1]\.\d+\.\d+|192\.168\.\d+\.\d+)$"
    )
    hostname = parsed_url.hostname
    if (hostname and ip_pattern.match(hostname)) or parsed_url.scheme == "file":
        return False
    return True

# Function to initialize browser and tabs
def initialize_browser_and_tabs():
    global browser_instance, tab_ids, connection_semaphore

    if CONFIG["DOCKER_MODE"]:
        options = ChromiumOptions()
        options.set_argument("--auto-open-devtools-for-tabs", "true")
        options.set_argument("--remote-debugging-port=9222")
        options.set_argument("--no-sandbox")
        options.set_argument("--disable-gpu")
        options.set_paths(browser_path=CONFIG["BROWSER_PATH"]).headless(CONFIG["HEADLESS"])
    else:
        options = ChromiumOptions()
        options.set_paths(browser_path=CONFIG["BROWSER_PATH"]).headless(CONFIG["HEADLESS"])
    
    for arg in CONFIG["CHROME_ARGUMENTS"]:
        options.set_argument(arg)
    
    options = ChromiumOptions().auto_port()

    browser_instance = ChromiumPage(addr_or_opts=options)
    
    for _ in range(CONFIG["NUM_TABS"]): 
        tab_id = browser_instance.new_tab()
        tab_ids.append(tab_id)
        tab_in_use[tab_id] = False
    
    # Initialize the semaphore to limit concurrent connections
    connection_semaphore = asyncio.Semaphore(CONFIG["MAX_CONNECTIONS"])

# Function to bypass Cloudflare protection
async def bypass_cloudflare(url: str, retries: int, log: bool, proxy: str = None) -> tuple:
    global browser_instance, connection_semaphore
    
    async with connection_semaphore:
        if browser_instance is None:
            initialize_browser_and_tabs()
        
        tab_id = get_next_tab()
        tab = browser_instance.get_tab(tab_id)
        
        try:
            tab.get(url)
            cf_bypasser = CloudflareBypasser(tab, retries, log)
            cf_bypasser.bypass()
            return tab, tab_id
        except Exception as e:
            release_tab(tab_id)  # Release the tab if there's an error
            raise e



@app.post("/raw_html_file")
async def get_raw_html_file(request: Request):
    data = await request.json()
    file_path = data.get("file_path")
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=400, detail="File not found")
    
    try:
        with open(file_path, 'r') as file:
            url = file.read().strip()
            print(f"URL: {url}")
        
        tab, tab_id = await bypass_cloudflare(url, 5, CONFIG["LOGGING"])
        html = tab.html
        cookies_json = {cookie.get("name", ""): cookie.get("value", " ") for cookie in tab.cookies()}
        
        response = Response(content=html, media_type="text/html")
        response.headers["cookies"] = json.dumps(cookies_json)
        response.headers["user_agent"] = tab.user_agent
        
        release_tab(tab_id)  # Release the tab when done
        return response
    except Exception as e:
        logger.error(f"Error in get_raw_html_file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/post_raw_html_file")
async def post_raw_html_file(request: Request):
    data = await request.json()
    
    logger.debug(f"Received data in post_raw_html_file: {data}")
    
    url_file_path = data.get("url_file_path")
    data_file_path = data.get("data_file_path")
    
    if not url_file_path or not data_file_path:
        raise HTTPException(
            status_code=400, 
            detail=f"Missing required parameters. Received: {data}"
        )
    
    if not os.path.exists(url_file_path):
        raise HTTPException(status_code=400, detail="URL file not found")
    
    if not os.path.exists(data_file_path):
        raise HTTPException(status_code=400, detail="Data file not found")
    
    try:
        # Read URL and data from files
        with open(url_file_path, 'r') as file:
            url = file.read().strip()
            print(f"URL: {url}")
        
        with open(data_file_path, 'r') as file:
            post_data = json.load(file)
            print(f"POST data: {post_data}")
        
        # Use the browser automation to bypass Cloudflare and send the POST request
        tab, tab_id = await bypass_cloudflare(url, 5, CONFIG["LOGGING"])
        
        # Execute a POST request in the browser context
        result = tab.execute_script(f"""
            (async () => {{
                const response = await fetch('{url}', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json'
                    }},
                    body: '{json.dumps(post_data).replace("'", "\\'")}'
                }});
                return await response.text();
            }})()
        """)
        
        cookies_json = {cookie.get("name", ""): cookie.get("value", " ") for cookie in tab.cookies()}
        
        response = Response(content=result, media_type="text/html")
        response.headers["cookies"] = json.dumps(cookies_json)
        response.headers["user_agent"] = tab.user_agent
        
        release_tab(tab_id)  # Release the tab when done
        return response
    except Exception as e:
        logger.error(f"Error in post_raw_html_file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))



# Clean up the browser instance and display on termination
def cleanup_resources():
    global browser_instance, display
    if browser_instance:
        browser_instance.quit()
    if display:
        display.stop()

# Register the cleanup function
atexit.register(cleanup_resources)

# Graceful shutdown handler
@app.on_event("shutdown")
async def shutdown_event():
    cleanup_resources()

# Initialize browser and display on startup
@app.on_event("startup")
async def startup_event():
    global display, browser_instance, tab_ids, connection_semaphore
    
    if (CONFIG["HEADLESS"] or CONFIG["DOCKER_MODE"]) and not display:
        display = Display(visible=0, size=(1920, 1080))
        display.start()
    
    if not browser_instance:
        initialize_browser_and_tabs()
    
    # Initialize the semaphore to limit concurrent connections
    connection_semaphore = asyncio.Semaphore(CONFIG["MAX_CONNECTIONS"])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cloudflare bypass API")
    parser.add_argument("--nolog", action="store_true", help="Disable logging")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.add_argument("--port", type=int, default=CONFIG["SERVER_PORT"], help="Port to run the server on")
    parser.add_argument("--max-connections", type=int, default=CONFIG["MAX_CONNECTIONS"], 
                       help="Maximum number of concurrent connections")
    args = parser.parse_args()

    CONFIG["LOGGING"] = not args.nolog
    CONFIG["HEADLESS"] = args.headless
    CONFIG["SERVER_PORT"] = args.port
    CONFIG["MAX_CONNECTIONS"] = args.max_connections

    # Run the server with uvicorn
    uvicorn.run(app, host="0.0.0.0", port=CONFIG["SERVER_PORT"], workers=1)

