import time
import random
import json
import os
import asyncio
import aiohttp
import uuid
from pathlib import Path
from typing import Dict, Optional, Tuple, List
from aiohttp_socks import ProxyConnector


try:
    # Import settings as module-level constants
    from settings import (
        REFRESH_INTERVAL,
        COOKIE_LIFETIME,
        MAX_COOKIES,
        COOKIES_DIR_PREFIX,
        BROWSER_PORTS_FILE,
        VERBOSE,
    )
except:
        # Import settings as module-level constants
    from .settings import (
        REFRESH_INTERVAL,
        COOKIE_LIFETIME,
        MAX_COOKIES,
        COOKIES_DIR_PREFIX,
        BROWSER_PORTS_FILE,
        VERBOSE,
    )

def load_browser_ports():
    ports_file = Path(os.path.expanduser(BROWSER_PORTS_FILE))
    if ports_file.exists():
        try:
            with open(ports_file, "r") as f:
                ports = json.load(f)
                if isinstance(ports, list):
                    return ports
        except Exception:
            pass
    return []

def get_cookies_dir(name: str) -> Path:
    base_dir = Path(__file__).parent / f"{COOKIES_DIR_PREFIX}{name}"
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir

def get_unique_cookie_filename() -> str:
    return f"{uuid.uuid4().hex}.json"

used_random_numbers = set()

def get_unique_random():
    global used_random_numbers
    current_time = int(time.time())
    while True:
        rand_num = random.randint(1, 1000000)
        if (rand_num, current_time // 86400) not in used_random_numbers:
            used_random_numbers.add((rand_num, current_time // 86400))
            return rand_num

def cleanup_used_numbers():
    global used_random_numbers
    current_day = int(time.time()) // 86400
    used_random_numbers = {(num, day) for num, day in used_random_numbers if day == current_day}

class CloudflareCookieManager:
    def __init__(
        self,
        name: str,
        generate_request_fn,
        refresh_interval: int = None,
        cookie_lifetime: int = None,
        max_cookies: int = None,
        verbose: bool = None,
    ):
        self.generate_request_fn = generate_request_fn
        self.refresh_interval = refresh_interval if refresh_interval is not None else REFRESH_INTERVAL
        self.cookie_lifetime = cookie_lifetime if cookie_lifetime is not None else COOKIE_LIFETIME
        self.max_cookies = max_cookies if max_cookies is not None else MAX_COOKIES
        self.verbose = verbose if verbose is not None else VERBOSE
        self.name = name

        self.browser_ports = load_browser_ports()
        self.cookie_monsters = ["🍪😋", "🍪🤤", "🍪😍", "🍪🤯", "🍪🥳"]
        self.cookies_dir = get_cookies_dir(self.name)

        self.last_get_cookie_time = None
        self._lock = asyncio.Lock()
        self.initialized = False

    def _log(self, level: str, message: str):
        if self.verbose:
            print(f"[{level.upper()}] {message}")

    async def initialize(self):
        if self.initialized:
            return
        await self._cleanup_expired_cookies()
        asyncio.create_task(self._periodic_cookie_refresh_and_cleanup())
        self.initialized = True
        self._log("info", f"Cookie manager initialized with {len(self.browser_ports)} ports")

    def _get_all_cookies_files(self) -> List[Path]:
        return list(self.cookies_dir.glob("*.json"))

    async def _cleanup_expired_cookies(self):
        current_time = time.time()
        expiration_time = current_time - self.cookie_lifetime

        removed = 0
        for cookie_file in self._get_all_cookies_files():
            try:
                with open(cookie_file, "r") as f:
                    cookie_data = json.load(f)
                timestamp = cookie_data.get("timestamp", 0)
                if timestamp < expiration_time:
                    cookie_file.unlink()
                    removed += 1
            except Exception as e:
                self._log("error", f"Failed to cleanup cookie {cookie_file}: {e}")
        if removed > 0:
            self._log("info", f"Expired cookies cleaned. Removed: {removed}")

    async def _get_cookie_count(self) -> int:
        return len(self._get_all_cookies_files())

    async def _has_cookies(self) -> bool:
        return (await self._get_cookie_count()) > 0

    async def _store_cookie_with_retry(self, cookie: Dict, max_retries: int = 5) -> bool:
        for attempt in range(max_retries):
            try:
                filename = self.cookies_dir / get_unique_cookie_filename()
                with open(filename, "w") as f:
                    json.dump(cookie, f)
                return True
            except Exception as e:
                self._log("error", f"Failed to store cookie on attempt {attempt + 1}: {e}")
                await asyncio.sleep(0.1 * (2 ** attempt))
        return False

    async def _periodic_cookie_refresh_and_cleanup(self):
        while True:
            try:
                await self._cleanup_expired_cookies()
                cookie_count = await self._get_cookie_count()
                if cookie_count < self.max_cookies:
                    ports = random.sample(self.browser_ports, min(len(self.browser_ports), self.max_cookies - cookie_count))
                    added = 0
                    for port in ports:
                        cookie = await self._fetch_new_cookie(port)
                        if cookie and await self._store_cookie_with_retry(cookie):
                            added += 1
                            if self.verbose:
                                self._log("info", f"{random.choice(self.cookie_monsters)} New cookie from port {port}!")
                    self._log("info", f"Added {added} cookies. Total: {cookie_count + added}")
                await asyncio.sleep(self.refresh_interval * random.uniform(1, 1.5))
            except Exception as e:
                self._log("error", f"Refresh cycle error: {e}")
                await asyncio.sleep(10)

    async def get_cookie(self, proxy_url: Optional[str] = None) -> Optional[Tuple[Dict, str]]:
        current_time = time.time()

        if self.last_get_cookie_time is None:
            self.last_get_cookie_time = current_time
            has_cookies = await self._has_cookies()
            if not has_cookies:
                await self.initialize()
        else:
            self.last_get_cookie_time = current_time

        cookie_files = self._get_all_cookies_files()
        if proxy_url:
            filtered_files = []
            for cf in cookie_files:
                try:
                    with open(cf, "r") as f:
                        data = json.load(f)
                    if data.get("proxy_url") == proxy_url:
                        filtered_files.append(cf)
                except Exception:
                    continue
            cookie_files = filtered_files

        if not cookie_files:
            return None

        selected_file = random.choice(cookie_files)
        try:
            with open(selected_file, "r") as f:
                cookie_data = json.load(f)
            cookie_id = selected_file.name
            return cookie_data, cookie_id
        except Exception as e:
            self._log("error", f"Failed to read cookie file {selected_file}: {e}")
            return None

    async def _fetch_new_cookie(self, port: int) -> Optional[Dict]:
        try:
            target_url, params = self.generate_request_fn()
            return await self._fetch_cookie_for_url(port, target_url, params)
        except Exception as e:
            self._log("error", f"Error fetching new cookie: {e}")
            return None

    async def _fetch_cookie_for_url(self, port: int, target_url: str, params: Dict[str, str],
                                    proxy_url: Optional[str] = None) -> Optional[Dict]:
        temp_file = f"/tmp/url_{get_unique_random()}.txt"
        try:
            with open(temp_file, 'w') as f:
                f.write(f"{target_url}?{'&'.join(f'{k}={v}' for k,v in params.items())}")

            session_args = {}
            if proxy_url:
                session_args['connector'] = ProxyConnector.from_url(proxy_url, rdns=True)

            async with aiohttp.ClientSession(**session_args) as session:
                async with session.post(f"http://localhost:{port}/raw_html_file",
                                        json={"file_path": temp_file}) as response:
                    if response.status != 200:
                        return None

                    cookies_json = response.headers.get("cookies")
                    user_agent = response.headers.get("user_agent")

                    if not cookies_json:
                        return None

                    return {
                        'cookies': json.loads(cookies_json),
                        'user_agent': user_agent,
                        'timestamp': time.time(),
                        'proxy_url': proxy_url
                    }
        except Exception as e:
            self._log("error", f"Error fetching cookie: {e}")
            return None
        finally:
            try:
                os.remove(temp_file)
            except Exception:
                pass

# Dictionary to store multiple cookie managers
_cookie_managers = {}

def get_cookie_manager(name: str, generate_request_fn, verbose: bool = None):
    global _cookie_managers
    if name not in _cookie_managers:
        _cookie_managers[name] = CloudflareCookieManager(
            name,
            generate_request_fn,
            verbose=verbose,
        )
    return _cookie_managers[name]

async def get_fresh_cookie_with_retries(
    name: str,
    generate_request_fn,
    verbose: bool = None,
    sleep_between_tries_s: float = 5,
    max_attempts: int = 20,
):
    cookie_manager = get_cookie_manager(name, generate_request_fn, verbose)
    cookie_result = None

    try:
        async with asyncio.timeout(2):
            cookie_result = await cookie_manager.get_cookie()
    except asyncio.TimeoutError:
        pass

    if cookie_result:
        return cookie_result

    for attempt in range(max_attempts):
        try:
            timeout_duration = min(3 * (1.5 ** attempt), 30)
            async with asyncio.timeout(timeout_duration):
                cookie_result = await cookie_manager.get_cookie()
            if not cookie_result:
                wait_time = sleep_between_tries_s * (1 + 0.5 * attempt)
                print(f"No cookies available, waiting for refresh... (Attempt {attempt + 1}/{max_attempts})")
                await asyncio.sleep(wait_time)
                continue
            else:
                break
        except asyncio.TimeoutError:
            print(f"Cookie retrieval timed out after {timeout_duration}s (Attempt {attempt + 1}/{max_attempts})")
            await asyncio.sleep(1)
            continue
        except Exception as e:
            print(f"Error retrieving cookie: {e} (Attempt {attempt + 1}/{max_attempts})")
            await asyncio.sleep(sleep_between_tries_s)
            continue

    if not cookie_result:
        raise Exception("Failed to get valid cloudflare cookies after all attempts")

    cookie_data, cookie_id = cookie_result
    return cookie_data, cookie_id
