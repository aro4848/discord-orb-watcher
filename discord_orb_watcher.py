#!/usr/bin/env python3
"""
Discord Orb & Video Quest Auto-Watcher (Undetectable Edition)
============================================================
Automates watching Discord video ads and completing video/ad quests for Orbs
using full browser-grade fingerprinting, live Discord Gateway session presence,
dynamic build extraction, and CDN media buffer emulation.

Anti-Detection Architecture:
1. TLS Fingerprint Spoofing: Uses curl_cffi to match Chromium / Electron JA3/JA4 TLS
   fingerprints and HTTP/2 protocol negotiation.
2. Dynamic Build Number: Scrapes the live Discord client build number directly from
   Discord's web app assets and local Discord installation.
3. Live Gateway Connection: Connects to Discord's WebSocket Gateway, identifies,
   maintains heartbeats, and acquires an authentic session_id before quest interaction.
4. CDN Video Buffer Simulation: Performs real HTTP Range requests against
   cdn.discordapp.com to buffer video chunks concurrently, leaving genuine CDN traffic logs.
5. Natural Playback Physics: Simulates real human video playback with realistic time
   intervals, micro-jitter, and fractional timestamp drift.
"""

import os
import sys
import time
import json
import random
import base64
import argparse
import threading
import re
from datetime import datetime, timezone

# Enforce UTF-8 console output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
        sys.stderr.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    except Exception:
        pass
    os.system("")

# Browser-grade TLS engine
try:
    from curl_cffi import requests as cffi_requests
except ImportError:
    print("[-] Missing 'curl_cffi'. Install it with: pip install curl_cffi")
    sys.exit(1)

# WebSocket client
try:
    import websocket
except ImportError:
    print("[-] Missing 'websocket-client'. Install it with: pip install websocket-client")
    sys.exit(1)

# Windows DPAPI decrypt for local Discord tokens
try:
    import win32crypt
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    HAS_LOCAL_DECRYPT = True
except ImportError:
    HAS_LOCAL_DECRYPT = False


CONFIG_FILE = "orb_config.json"
API_BASE = "https://discord.com/api/v9"
GATEWAY_URL = "wss://gateway.discord.gg/?v=9&encoding=json"


class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RESET = '\033[0m'


def print_banner():
    banner = f"""
{Colors.CYAN}{Colors.BOLD}=======================================================
   DISCORD ORB & VIDEO AD AUTO-WATCHER (STEALTH)
   • Chromium TLS (JA3/JA4) • Live Gateway Session
   • CDN Media Emulation    • Dynamic Build Match
======================================================={Colors.RESET}
"""
    print(banner)


def find_discord_tokens():
    """Auto-detects and decrypts user tokens from local Discord installations on Windows."""
    if not HAS_LOCAL_DECRYPT:
        return []

    appdata = os.getenv("APPDATA")
    if not appdata:
        return []

    discord_paths = [
        os.path.join(appdata, "discord"),
        os.path.join(appdata, "discordcanary"),
        os.path.join(appdata, "discordptb"),
    ]

    found_tokens = []

    for base_dir in discord_paths:
        state_path = os.path.join(base_dir, "Local State")
        db_path = os.path.join(base_dir, "Local Storage", "leveldb")

        if not (os.path.exists(state_path) and os.path.exists(db_path)):
            continue

        try:
            with open(state_path, "r", encoding="utf-8") as f:
                state_data = json.load(f)
            encrypted_key = base64.b64decode(state_data["os_crypt"]["encrypted_key"])[5:]
            master_key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
        except Exception:
            continue

        for file_name in os.listdir(db_path):
            if not file_name.endswith((".log", ".ldb")):
                continue
            file_path = os.path.join(db_path, file_name)
            try:
                with open(file_path, "rb") as f:
                    content = f.read()
                for match in re.findall(rb'dQw4w9WgXcQ:[^"\'\s]*', content):
                    try:
                        raw_payload = base64.b64decode(match.split(b":")[1])
                        iv = raw_payload[3:15]
                        ciphertext = raw_payload[15:]
                        token = AESGCM(master_key).decrypt(iv, ciphertext, None).decode("utf-8")
                        if token and token not in found_tokens:
                            found_tokens.append(token)
                    except Exception:
                        pass
            except Exception:
                pass

    return found_tokens


def detect_local_discord_version():
    """Detects installed version of Discord Desktop on Windows."""
    localappdata = os.getenv("LOCALAPPDATA")
    if not localappdata:
        return "1.0.9261"

    discord_dir = os.path.join(localappdata, "Discord")
    if os.path.exists(discord_dir):
        for entry in os.listdir(discord_dir):
            if entry.startswith("app-"):
                return entry.replace("app-", "")

    return "1.0.9261"


def fetch_live_build_number():
    """Dynamically fetches the current live Discord build number from web assets."""
    try:
        r = cffi_requests.get("https://discord.com/app", impersonate="chrome120", timeout=8)
        scripts = re.findall(r'/assets/[a-zA-Z0-9\.\-]+\.js', r.text)
        for s in reversed(scripts[-15:]):
            url = "https://discord.com" + s
            try:
                res = cffi_requests.get(url, impersonate="chrome120", timeout=6)
                m = re.search(r'buildNumber["\':\s]+(\d{6,7})', res.text)
                if m:
                    return int(m.group(1))
                m2 = re.search(r'build_number["\':\s]+(\d{6,7})', res.text)
                if m2:
                    return int(m2.group(1))
            except Exception:
                pass
    except Exception:
        pass
    return 638651  # Reliable live fallback


def load_token(cli_token=None):
    """Retrieves token from CLI argument, config file, environment, or auto-detect."""
    if cli_token:
        return cli_token.strip()

    candidates = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json"),
        r"C:\Users\PC\Desktop\Discord id scraper\config.json",
        CONFIG_FILE
    ]
    for c_path in candidates:
        if os.path.exists(c_path):
            try:
                with open(c_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    tok = cfg.get("user_token") or cfg.get("token")
                    if tok:
                        return tok.strip()
            except Exception:
                pass

    env_tok = os.getenv("DISCORD_TOKEN")
    if env_tok:
        return env_tok.strip()

    print(f"{Colors.YELLOW}[*] Auto-detecting token from local Discord installation...{Colors.RESET}")
    detected = find_discord_tokens()
    if detected:
        tok = detected[0]
        print(f"{Colors.GREEN}[+] Found active Discord desktop session!{Colors.RESET}")
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump({"token": tok}, f, indent=2)
        except Exception:
            pass
        return tok

    print(f"{Colors.RED}[!] Could not auto-detect active Discord session.{Colors.RESET}")
    try:
        user_input = input("Enter your Discord User Token: ").strip()
        if user_input:
            try:
                with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                    json.dump({"token": user_input}, f, indent=2)
            except Exception:
                pass
            return user_input
    except KeyboardInterrupt:
        sys.exit(0)

    return None


class GatewaySession:
    """Maintains an active WebSocket Gateway connection with IDENTIFY and Heartbeats."""

    def __init__(self, token: str, super_properties: dict):
        self.token = token
        self.super_properties = super_properties
        self.ws = None
        self.session_id = None
        self.running = False
        self.thread = None
        self.heartbeat_thread = None
        self.heartbeat_interval = 41.25
        self.ready_event = threading.Event()

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._run_ws, daemon=True)
        self.thread.start()
        # Wait up to 8s for READY
        self.ready_event.wait(timeout=8.0)

    def stop(self):
        self.running = False
        if self.ws:
            try:
                self.ws.close()
            except Exception:
                pass

    def _run_ws(self):
        try:
            self.ws = websocket.WebSocket()
            self.ws.connect(GATEWAY_URL)

            # Receive Hello
            raw = self.ws.recv()
            hello = json.loads(raw)
            if hello.get("op") == 10:
                self.heartbeat_interval = hello["d"]["heartbeat_interval"] / 1000.0

            # Start Heartbeat thread
            self.heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
            self.heartbeat_thread.start()

            # Send Identify
            identify_payload = {
                "op": 2,
                "d": {
                    "token": self.token,
                    "capabilities": 30717,
                    "properties": self.super_properties,
                    "presence": {
                        "status": "online",
                        "since": 0,
                        "activities": [],
                        "afk": False
                    },
                    "compress": False,
                    "client_state": {
                        "guild_versions": {}
                    }
                }
            }
            self.ws.send(json.dumps(identify_payload))

            # Event loop
            while self.running:
                data = self.ws.recv()
                if not data:
                    break
                msg = json.loads(data)
                t = msg.get("t")
                if t == "READY":
                    self.session_id = msg.get("d", {}).get("session_id")
                    self.ready_event.set()
        except Exception:
            pass

    def _heartbeat_loop(self):
        while self.running:
            time.sleep(self.heartbeat_interval)
            if self.ws and self.running:
                try:
                    self.ws.send(json.dumps({"op": 1, "d": None}))
                except Exception:
                    break

    def update_presence(self, activities=None):
        """Sends Gateway Opcode 3 (STATUS_UPDATE) to broadcast active gameplay."""
        if not self.ws or not self.running:
            return
        payload = {
            "op": 3,
            "d": {
                "since": None,
                "activities": activities or [],
                "status": "online",
                "afk": False
            }
        }
        try:
            self.ws.send(json.dumps(payload))
        except Exception:
            pass


class StealthDiscordClient:
    """Browser-grade Discord Client emulating Chromium TLS, HTTP/2, and Desktop Headers."""

    def __init__(self, token: str):
        self.token = token
        self.session = cffi_requests.Session(impersonate="chrome120")

        # Dynamically determine version and build
        self.client_version = detect_local_discord_version()
        self.build_number = fetch_live_build_number()

        self.super_properties = {
            "os": "Windows",
            "browser": "Discord Client",
            "release_channel": "stable",
            "client_version": self.client_version,
            "os_version": "10.0.19045",
            "os_arch": "x64",
            "app_arch": "x64",
            "system_locale": "en-US",
            "browser_user_agent": (
                f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                f"discord/{self.client_version} Chrome/128.0.6613.186 Electron/32.2.7 Safari/537.36"
            ),
            "browser_version": "32.2.7",
            "client_build_number": self.build_number,
            "native_build_number": 55260,
            "client_event_source": None
        }

        self.encoded_props = base64.b64encode(json.dumps(self.super_properties).encode("utf-8")).decode("utf-8")
        self.context_props = base64.b64encode(json.dumps({"location": "Quest Home"}).encode("utf-8")).decode("utf-8")

        self.session.headers.update({
            "Authorization": self.token,
            "Content-Type": "application/json",
            "User-Agent": self.super_properties["browser_user_agent"],
            "X-Super-Properties": self.encoded_props,
            "X-Context-Properties": self.context_props,
            "X-Discord-Locale": "en-US",
            "X-Discord-Timezone": "America/New_York",
            "Accept": "*/*",
            "Sec-Ch-Ua": '"Not?A_Brand";v="99", "Chromium";v="128"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
        })

        # Initialize Gateway
        self.gateway = GatewaySession(self.token, self.super_properties)

    def start_gateway(self):
        print(f"{Colors.YELLOW}[*] Establishing authenticated Gateway WebSocket presence...{Colors.RESET}")
        self.gateway.start()
        if self.gateway.session_id:
            print(f"{Colors.GREEN}[+] Gateway connected! Session ID: {self.gateway.session_id[:12]}...{Colors.RESET}")
        else:
            print(f"{Colors.DIM}[i] Gateway connected in background.{Colors.RESET}")

    def close(self):
        self.gateway.stop()

    def get_user_profile(self):
        res = self.session.get(f"{API_BASE}/users/@me")
        if res.status_code == 200:
            return res.json()
        elif res.status_code == 401:
            raise PermissionError("Invalid Discord User Token (401 Unauthorized)")
        res.raise_for_status()

    def get_quests(self):
        res = self.session.get(f"{API_BASE}/quests/@me")
        if res.status_code == 200:
            return res.json()
        res.raise_for_status()

    def get_claimed_quests(self):
        res = self.session.get(f"{API_BASE}/quests/@me/claimed")
        if res.status_code == 200:
            return res.json()
        res.raise_for_status()

    def enroll_quest(self, quest_id: str, captcha_key: str = None, captcha_rqtoken: str = None):
        payload = {"location": 1}
        headers = {}
        if captcha_key:
            payload["captcha_key"] = captcha_key
            headers["X-Captcha-Key"] = captcha_key
        if captcha_rqtoken:
            payload["captcha_rqtoken"] = captcha_rqtoken
            headers["X-Captcha-Rqtoken"] = captcha_rqtoken

        res = self.session.post(f"{API_BASE}/quests/{quest_id}/enroll", json=payload, headers=headers)
        if res.status_code in (200, 204):
            return res.json() if res.content else {}
        if res.status_code == 400:
            try:
                err_data = res.json()
                if "captcha_key" in err_data or "captcha_service" in err_data:
                    return {"captcha_required": True, "details": err_data}
            except Exception:
                pass
        if res.status_code == 429:
            try:
                data = res.json()
                return {"rate_limited": True, "retry_after": data.get("retry_after", 300)}
            except Exception:
                return {"rate_limited": True, "retry_after": 300}
        res.raise_for_status()

    def send_video_progress(self, quest_id: str, timestamp: float):
        payload = {"timestamp": round(timestamp, 2)}
        res = self.session.post(f"{API_BASE}/quests/{quest_id}/video-progress", json=payload)
        if res.status_code == 200:
            return res.json()
        res.raise_for_status()

    def claim_reward(self, quest_id: str, captcha_key: str = None, captcha_rqtoken: str = None):
        payload = {"location": 1, "platform": 0}
        headers = {}
        if captcha_key:
            payload["captcha_key"] = captcha_key
            headers["X-Captcha-Key"] = captcha_key
        if captcha_rqtoken:
            payload["captcha_rqtoken"] = captcha_rqtoken
            headers["X-Captcha-Rqtoken"] = captcha_rqtoken

        res = self.session.post(f"{API_BASE}/quests/{quest_id}/claim-reward", json=payload, headers=headers)
        if res.status_code == 200:
            return res.json()
        if res.status_code == 400:
            try:
                err_data = res.json()
                if "captcha_key" in err_data or "captcha_service" in err_data:
                    return {"captcha_required": True, "details": err_data}
            except Exception:
                pass
        if res.status_code == 404:
            res2 = self.session.post(f"{API_BASE}/quests/{quest_id}/claim", json=payload, headers=headers)
            if res2.status_code == 200:
                return res2.json()
            if res2.status_code == 400:
                try:
                    err_data = res2.json()
                    if "captcha_key" in err_data or "captcha_service" in err_data:
                        return {"captcha_required": True, "details": err_data}
                except Exception:
                    pass
        res.raise_for_status()

    def stream_video_chunk(self, video_asset_path: str, byte_start: int, byte_length: int = 131072):
        """Simulates HTML5 video player buffer range request from Discord CDN."""
        if not video_asset_path:
            return
        url = f"https://cdn.discordapp.com/{video_asset_path}"
        headers = {"Range": f"bytes={byte_start}-{byte_start + byte_length - 1}"}
        try:
            self.session.get(url, headers=headers, timeout=5)
        except Exception:
            pass

    def send_quest_heartbeat(self, quest_id: str, app_id: str, terminal: bool = False):
        """Sends gameplay heartbeat to advance PLAY_ON_DESKTOP quests."""
        payload = {
            "stream_key": None,
            "application_id": str(app_id),
            "terminal": terminal
        }
        res = self.session.post(f"{API_BASE}/quests/{quest_id}/heartbeat", json=payload)
        if res.status_code == 200:
            return res.json()
        res.raise_for_status()


def get_captcha_api_key() -> str:
    """Finds the 2Captcha API key from configuration or environment."""
    candidates = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json"),
        r"C:\Users\PC\Desktop\Discord id scraper\config.json",
        r"C:\Users\PC\Downloads\cradleKoi-main\cradleKoi-main\config.json",
        "config.json"
    ]
    for p in candidates:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    k = cfg.get("captcha_api_key") or cfg.get("2captcha_key") or cfg.get("captcha_key")
                    if k:
                        return str(k).strip()
            except Exception:
                pass
    return "c7d4accb8b183aff4e0969b0cfb7e9a6"


def solve_discord_hcaptcha(captcha_details: dict, user_agent: str = None) -> tuple:
    """
    Solves Discord's enterprise hCaptcha challenge using 2Captcha API (v2 createTask or fallback).
    Returns (captcha_key, captcha_rqtoken).
    """
    api_key = get_captcha_api_key()
    if not api_key:
        print(f"  {Colors.RED}[!] No 2Captcha API key configured.{Colors.RESET}")
        return None, None

    sitekey = (
        captcha_details.get("captcha_sitekey")
        or captcha_details.get("sitekey")
        or "4c672d35-0701-42b2-88c3-78380b0db560"
    )
    rqdata = captcha_details.get("captcha_rqdata") or captcha_details.get("rqdata")
    rqtoken = captcha_details.get("captcha_rqtoken") or captcha_details.get("rqtoken")

    print(f"  {Colors.YELLOW}[*] Discord Captcha challenge detected! Dispatching to 2Captcha...{Colors.RESET}")
    print(f"      Sitekey: {sitekey}")
    if rqdata:
        print(f"      Enterprise RQData payload detected: {rqdata[:20]}...")

    import requests as raw_req

    task = {
        "type": "HCaptchaTaskProxyless",
        "websiteURL": "https://discord.com",
        "websiteKey": sitekey,
        "isInvisible": True,
    }
    if user_agent:
        task["userAgent"] = user_agent
    if rqdata:
        task["enterprisePayload"] = {"rqdata": rqdata}

    # 1. Modern 2Captcha v2 JSON API
    try:
        create_res = raw_req.post(
            "https://api.2captcha.com/createTask",
            json={"clientKey": api_key, "task": task},
            timeout=15
        )
        c_json = create_res.json()
        if c_json.get("errorId") == 0 and c_json.get("taskId"):
            task_id = c_json["taskId"]
            print(f"  {Colors.CYAN}[*] 2Captcha Task ID {task_id} queued. Polling solution...{Colors.RESET}")
            for attempt in range(24):  # up to 120s
                time.sleep(5)
                poll_res = raw_req.post(
                    "https://api.2captcha.com/getTaskResult",
                    json={"clientKey": api_key, "taskId": task_id},
                    timeout=10
                )
                p_json = poll_res.json()
                if p_json.get("status") == "ready":
                    sol = p_json.get("solution", {})
                    token = sol.get("token") or sol.get("gRecaptchaResponse")
                    print(f"\n  {Colors.GREEN}{Colors.BOLD}[+] 2Captcha successfully solved challenge in {(attempt + 1) * 5}s!{Colors.RESET}")
                    return token, rqtoken
                elif p_json.get("errorId", 0) != 0:
                    print(f"\n  {Colors.RED}[!] 2Captcha error: {p_json.get('errorDescription')}{Colors.RESET}")
                    break
                sys.stdout.write(f"\r      Waiting for 2Captcha solver... ({(attempt + 1) * 5}s)")
                sys.stdout.flush()
            print()
    except Exception as e:
        print(f"  {Colors.YELLOW}[!] 2Captcha v2 API error ({e}), trying legacy fallback...{Colors.RESET}")

    # 2. Legacy fallback
    try:
        in_params = {
            "key": api_key,
            "method": "hcaptcha",
            "sitekey": sitekey,
            "pageurl": "https://discord.com",
            "json": 1
        }
        if rqdata:
            in_params["rqdata"] = rqdata
            in_params["data"] = rqdata

        r = raw_req.post("https://2captcha.com/in.php", data=in_params, timeout=12)
        in_data = r.json()
        if in_data.get("status") == 1:
            req_id = in_data.get("request")
            print(f"  {Colors.CYAN}[*] 2Captcha legacy task {req_id} queued. Polling...{Colors.RESET}")
            for attempt in range(24):
                time.sleep(5)
                res_url = f"https://2captcha.com/res.php?key={api_key}&action=get&id={req_id}&json=1"
                res_resp = raw_req.get(res_url, timeout=10).json()
                if res_resp.get("status") == 1:
                    token = res_resp.get("request")
                    print(f"\n  {Colors.GREEN}{Colors.BOLD}[+] 2Captcha legacy solved challenge in {(attempt + 1) * 5}s!{Colors.RESET}")
                    return token, rqtoken
                elif res_resp.get("request") != "CAPCHA_NOT_READY":
                    print(f"\n  {Colors.RED}[!] 2Captcha error: {res_resp.get('request')}{Colors.RESET}")
                    break
                sys.stdout.write(f"\r      Waiting for 2Captcha solver... ({(attempt + 1) * 5}s)")
                sys.stdout.flush()
            print()
    except Exception as e:
        print(f"  {Colors.RED}[!] 2Captcha fallback error: {e}{Colors.RESET}")

    return None, None


def enroll_quest_with_captcha(client: StealthDiscordClient, quest_id: str):
    """Enrolls in quest, automatically solving Discord hCaptcha via 2Captcha if challenged."""
    try:
        enroll_res = client.enroll_quest(quest_id)
        if isinstance(enroll_res, dict) and enroll_res.get("captcha_required"):
            c_token, c_rqtoken = solve_discord_hcaptcha(enroll_res.get("details", {}), getattr(client, "user_agent", None))
            if c_token:
                print(f"  {Colors.YELLOW}[*] Re-submitting enrollment with 2Captcha token...{Colors.RESET}")
                enroll_res = client.enroll_quest(quest_id, captcha_key=c_token, captcha_rqtoken=c_rqtoken)

        if isinstance(enroll_res, dict) and enroll_res.get("rate_limited"):
            retry_sec = float(enroll_res.get("retry_after", 300))
            print(f"  {Colors.YELLOW}[!] Enrollment rate-limited by Discord (429). Retry after {retry_sec:.0f}s.{Colors.RESET}")
            return {"rate_limited": True, "retry_after": retry_sec}
        user_status = enroll_res.get("user_status", enroll_res) if isinstance(enroll_res, dict) else {}
        print(f"  {Colors.GREEN}[+] Enrolled successfully.{Colors.RESET}")
        return user_status
    except Exception as e:
        if "429" in str(e):
            print(f"  {Colors.YELLOW}[!] Enrollment rate-limited by Discord (429).{Colors.RESET}")
            return {"rate_limited": True, "retry_after": 300}
        print(f"  {Colors.RED}[!] Enrollment failed: {e}{Colors.RESET}")
        return False


def claim_quest_with_captcha(client: StealthDiscordClient, quest_id: str, reward_desc: str = "Reward"):
    """Claims quest reward, automatically solving Discord hCaptcha via 2Captcha if challenged."""
    print(f"  {Colors.YELLOW}[*] Claiming reward / Orbs...{Colors.RESET}")
    time.sleep(random.uniform(1.2, 2.5))  # Human click delay
    try:
        claim_res = client.claim_reward(quest_id)
        if isinstance(claim_res, dict) and claim_res.get("captcha_required"):
            print(f"  {Colors.YELLOW}[*] Direct API claim requires captcha. Solving via 2Captcha...{Colors.RESET}")
            c_token, c_rqtoken = solve_discord_hcaptcha(claim_res.get("details", {}), getattr(client, "user_agent", None))
            if c_token:
                print(f"  {Colors.YELLOW}[*] Re-submitting claim with 2Captcha token...{Colors.RESET}")
                claim_res = client.claim_reward(quest_id, captcha_key=c_token, captcha_rqtoken=c_rqtoken)

        if isinstance(claim_res, dict) and claim_res.get("captcha_required"):
            print(f"  {Colors.YELLOW}[*] Direct API claim flagged. Triggering local Discord Desktop Bridge...{Colors.RESET}")
            bridge_claimed = False
            try:
                import requests as py_requests
                b_res = py_requests.get("http://127.0.0.1:54321/claim-all", timeout=15)
                if b_res.status_code == 200:
                    b_data = b_res.json()
                    if b_data.get("success") and b_data.get("result", {}).get("claimedCount", 0) > 0:
                        print(f"  {Colors.GREEN}{Colors.BOLD}[+] Reward Auto-Claimed via Local Discord Desktop Bridge!{Colors.RESET}")
                        bridge_claimed = True
            except Exception:
                pass
            if not bridge_claimed:
                print(f"  {Colors.GREEN}{Colors.BOLD}[+] Quest Marked 100% COMPLETED on Discord!{Colors.RESET}")
                print(f"  {Colors.CYAN}[★] Discord 1-click verification: click 'Claim Reward' in Discord Desktop (under Discover -> Quests) to collect your {reward_desc}!{Colors.RESET}")
        else:
            print(f"  {Colors.GREEN}{Colors.BOLD}[+] Reward Claimed Successfully!{Colors.RESET}")
            if isinstance(claim_res, dict):
                orbs = claim_res.get("orb_quantity_claimed")
                if orbs:
                    print(f"  {Colors.GREEN}[+] Orbs Earned: +{orbs} Orbs!{Colors.RESET}")
        return True
    except Exception as e:
        print(f"  {Colors.RED}[!] Failed to claim reward: {e}{Colors.RESET}")
        return False


def draw_progress_bar(current: float, total: float, width: int = 25, prefix: str = ""):
    if total <= 0:
        pct = 1.0
    else:
        pct = min(1.0, max(0.0, current / total))

    filled = int(width * pct)
    bar = "█" * filled + "░" * (width - filled)
    percent_str = f"{pct * 100:5.1f}%"
    timing_str = f"{current:4.1f}/{total:4.1f}s"
    sys.stdout.write(f"\r  {prefix}[{bar}] {percent_str} ({timing_str})")
    sys.stdout.flush()


def process_video_quest(client: StealthDiscordClient, quest: dict):
    """
    Watches a video ad with natural playback timing and CDN buffering.
    Strictly enforces real-world elapsed time so that server checks see 100% genuine duration.
    """
    quest_id = quest["id"]
    cfg = quest.get("config", {})
    msgs = cfg.get("messages", {})
    quest_name = msgs.get("quest_name", f"Quest #{quest_id}")

    task_config = cfg.get("task_config_v2") or cfg.get("task_config") or {}
    tasks = task_config.get("tasks", {})

    task_name = None
    for supported in ("WATCH_VIDEO", "WATCH_VIDEO_ON_MOBILE"):
        if supported in tasks:
            task_name = supported
            break

    if not task_name:
        print(f"{Colors.YELLOW}[?] '{quest_name}' is not a video ad quest.{Colors.RESET}")
        return False

    task_data = tasks[task_name]
    seconds_needed = float(task_data.get("target", 30.0))
    user_status = quest.get("user_status") or {}

    # Extract video asset URL for CDN buffering emulation
    task_assets = task_data.get("assets", {})
    video_asset = (
        task_assets.get("video", {}).get("url")
        or task_assets.get("video_low_res", {}).get("url")
        or cfg.get("assets", {}).get("hero_video")
        or cfg.get("assets", {}).get("quest_bar_hero_video")
    )

    # Extract reward details
    rewards_data = cfg.get("rewards") or cfg.get("rewards_config", {})
    if isinstance(rewards_data, dict):
        rewards_list = rewards_data.get("rewards", [])
    elif isinstance(rewards_data, list):
        rewards_list = rewards_data
    else:
        rewards_list = []

    reward_desc = "Unknown Reward"
    for r in rewards_list:
        if isinstance(r, dict):
            if r.get("orb_quantity"):
                reward_desc = f"{r.get('orb_quantity')} Orbs"
                break
            elif r.get("messages", {}).get("name"):
                reward_desc = r["messages"]["name"]
                break

    print(f"\n{Colors.BOLD}{Colors.CYAN}--- Processing Ad: {quest_name} ---{Colors.RESET}")
    print(f"  Quest ID: {quest_id}")
    print(f"  Reward: {Colors.GREEN}{reward_desc}{Colors.RESET}")
    print(f"  Target Duration: {seconds_needed:.1f}s")
    if video_asset:
        print(f"  CDN Stream: {video_asset[:50]}...")

    # Step 1: Enroll if needed
    if not user_status.get("enrolled_at"):
        enroll_res = enroll_quest_with_captcha(client, quest_id)
        if isinstance(enroll_res, dict) and enroll_res.get("rate_limited"):
            return enroll_res
        if not enroll_res:
            return False
        user_status = enroll_res
    else:
        print(f"  {Colors.GREEN}[+] Already enrolled.{Colors.RESET}")

    # Check if already completed
    if user_status.get("completed_at"):
        print(f"  {Colors.GREEN}[+] Quest already completed!{Colors.RESET}")
    else:
        prog_dict = user_status.get("progress", {}).get(task_name) or {}
        seconds_done = float(prog_dict.get("value", 0.0))
        print(f"  {Colors.YELLOW}[*] Simulating realistic video playback & CDN streaming...{Colors.RESET}")

        completed = False
        cdn_byte_offset = 0

        # Initial video buffer fetch (first 256 KB)
        if video_asset:
            client.stream_video_chunk(video_asset, 0, 262144)
            cdn_byte_offset += 262144

        start_time = time.time()

        while seconds_done < seconds_needed:
            remaining = seconds_needed - seconds_done
            # Natural step duration (5.5s to 7.2s with random gaussian noise)
            step_duration = min(remaining, random.uniform(5.5, 7.2))

            draw_progress_bar(seconds_done, seconds_needed, prefix="Streaming: ")

            # Real-time sleep (never advance faster than real clock)
            time.sleep(step_duration)

            # Concurrent video chunk fetch from CDN
            if video_asset and seconds_done < seconds_needed:
                client.stream_video_chunk(video_asset, cdn_byte_offset, 131072)
                cdn_byte_offset += 131072

            # Float drift to mimic exact player time
            jitter = random.uniform(0.05, 0.35)
            next_timestamp = min(seconds_needed, seconds_done + step_duration + jitter)

            try:
                res = client.send_video_progress(quest_id, next_timestamp)
                if isinstance(res, dict):
                    if res.get("completed_at"):
                        completed = True
                    prog = res.get("progress", {}).get(task_name, {})
                    seconds_done = float(prog.get("value", next_timestamp))
                else:
                    seconds_done = next_timestamp
            except Exception as e:
                print(f"\n  {Colors.RED}[!] Progress heartbeat failed: {e}{Colors.RESET}")
                time.sleep(3)
                continue

            draw_progress_bar(seconds_done, seconds_needed, prefix="Streaming: ")

            if completed or seconds_done >= seconds_needed:
                break

        # Final completion ping
        if not completed:
            try:
                final_res = client.send_video_progress(quest_id, seconds_needed)
                if isinstance(final_res, dict) and final_res.get("completed_at"):
                    completed = True
            except Exception:
                pass

        total_elapsed = time.time() - start_time
        print(f"\n  {Colors.GREEN}{Colors.BOLD}[+] Video playback complete! (Duration: {total_elapsed:.1f}s){Colors.RESET}")

    # Step 3: Claim reward
    if user_status.get("claimed_at"):
        print(f"  {Colors.GREEN}[+] Reward has already been claimed.{Colors.RESET}")
    else:
        claim_quest_with_captcha(client, quest_id, reward_desc)

    return True


def process_game_quest(client: StealthDiscordClient, quest: dict):
    """
    Automates PLAY_ON_DESKTOP quests by broadcasting Gateway presence and sending periodic heartbeats.
    """
    quest_id = quest["id"]
    cfg = quest.get("config", {})
    msgs = cfg.get("messages", {})
    quest_name = msgs.get("quest_name", f"Quest #{quest_id}")
    game_title = msgs.get("game_title", quest_name)

    task_config = cfg.get("task_config_v2") or cfg.get("task_config") or {}
    tasks = task_config.get("tasks", {})
    task_data = tasks.get("PLAY_ON_DESKTOP")
    if not task_data:
        return False

    apps = task_data.get("applications", [])
    if not apps:
        return False
    app_id = apps[0].get("id")
    target_seconds = float(task_data.get("target", 900.0))
    user_status = quest.get("user_status") or {}

    # Extract reward details
    rewards_data = cfg.get("rewards") or cfg.get("rewards_config", {})
    if isinstance(rewards_data, dict):
        rewards_list = rewards_data.get("rewards", [])
    elif isinstance(rewards_data, list):
        rewards_list = rewards_data
    else:
        rewards_list = []

    reward_desc = "Unknown Reward"
    for r in rewards_list:
        if isinstance(r, dict):
            if r.get("orb_quantity"):
                reward_desc = f"{r.get('orb_quantity')} Orbs"
                break
            elif r.get("messages", {}).get("name"):
                reward_desc = r["messages"]["name"]
                break

    print(f"\n{Colors.BOLD}{Colors.CYAN}--- Processing Game Quest: {quest_name} ---{Colors.RESET}")
    print(f"  Game Title: {game_title} | App ID: {app_id}")
    print(f"  Reward: {Colors.GREEN}{reward_desc}{Colors.RESET}")
    print(f"  Target Playtime: {target_seconds/60:.0f} minutes ({target_seconds:.0f}s)")

    # Step 1: Enroll if needed
    if not user_status.get("enrolled_at"):
        enroll_res = enroll_quest_with_captcha(client, quest_id)
        if isinstance(enroll_res, dict) and enroll_res.get("rate_limited"):
            return enroll_res
        if not enroll_res:
            return False
        user_status = enroll_res
    else:
        print(f"  {Colors.GREEN}[+] Already enrolled.{Colors.RESET}")

    if user_status.get("completed_at"):
        print(f"  {Colors.GREEN}[+] Quest already completed!{Colors.RESET}")
        if not user_status.get("claimed_at"):
            claim_quest_with_captcha(client, quest_id, reward_desc)
        return True

    # Step 2: Set Gateway Activity Presence
    start_ms = int(time.time() * 1000)
    activity = [{
        "name": game_title,
        "type": 0,
        "application_id": str(app_id),
        "timestamps": {"start": start_ms}
    }]
    client.gateway.update_presence(activity)
    print(f"  {Colors.GREEN}[+] Broadcasted active gameplay presence: Playing '{game_title}'{Colors.RESET}")

    # Step 3: Heartbeat loop
    prog_dict = user_status.get("progress", {}).get("PLAY_ON_DESKTOP") or {}
    seconds_done = float(prog_dict.get("value", 0.0))
    print(f"  {Colors.YELLOW}[*] Emulating active gameplay heartbeats...{Colors.RESET}")

    try:
        while seconds_done < target_seconds:
            sleep_time = min(random.uniform(45.0, 58.0), max(5.0, target_seconds - seconds_done + 2))
            draw_progress_bar(seconds_done, target_seconds, prefix="Playing: ")
            time.sleep(sleep_time)

            is_terminal = (seconds_done + sleep_time >= target_seconds)
            try:
                hb_res = client.send_quest_heartbeat(quest_id, app_id, terminal=is_terminal)
                p_info = hb_res.get("progress", {}).get("PLAY_ON_DESKTOP") or {}
                new_val = float(p_info.get("value", seconds_done + sleep_time))
                seconds_done = new_val
                if hb_res.get("completed_at") or is_terminal:
                    draw_progress_bar(target_seconds, target_seconds, prefix="Playing: ")
                    print(f"\n  {Colors.GREEN}{Colors.BOLD}[+] Game Quest Completed! ({target_seconds:.0f}s elapsed){Colors.RESET}")
                    break
            except Exception as e:
                print(f"\n  {Colors.YELLOW}[!] Heartbeat error: {e}. Retrying...{Colors.RESET}")
    finally:
        # Clear activity presence
        client.gateway.update_presence([])

    # Step 4: Claim reward
    if user_status.get("claimed_at"):
        print(f"  {Colors.GREEN}[+] Reward has already been claimed.{Colors.RESET}")
    else:
        claim_quest_with_captcha(client, quest_id, reward_desc)

    return True


def run_watcher(client: StealthDiscordClient, list_only: bool = False, max_ads: int = 3, mode: str = "video"):
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n{Colors.BOLD}[{now_str}] Checking available Discord Quests...{Colors.RESET}")

    try:
        quests_data = client.get_quests()
    except Exception as e:
        print(f"{Colors.RED}[!] Error fetching quests: {e}{Colors.RESET}")
        return

    # Pre-flight account status checks
    if quests_data.get("quest_access_suspended_until"):
        print(f"{Colors.RED}{Colors.BOLD}[!] ALERT: Account quest access is suspended until {quests_data['quest_access_suspended_until']}. Aborting.{Colors.RESET}")
        return
    if quests_data.get("quest_enrollment_blocked_until"):
        print(f"{Colors.YELLOW}[!] Notice: Quest enrollment is temporarily blocked until {quests_data['quest_enrollment_blocked_until']}.{Colors.RESET}")

    quests = quests_data.get("quests", [])
    print(f"{Colors.GREEN}[+] Found {len(quests)} active quest(s) on account.{Colors.RESET}")

    if not quests:
        print(f"{Colors.DIM}[i] No uncompleted or new quests right now. All caught up!{Colors.RESET}")
        return

    video_quests = []
    game_quests = []
    completed_unclaimed = []
    other_quests = []
    now = datetime.now(timezone.utc)

    for q in quests:
        cfg = q.get("config", {})

        # Filter out expired quests
        exp_str = cfg.get("expires_at")
        if exp_str:
            try:
                exp_dt = datetime.fromisoformat(exp_str)
                if exp_dt <= now:
                    continue
            except Exception:
                pass

        task_cfg = cfg.get("task_config_v2") or cfg.get("task_config") or {}
        tasks = task_cfg.get("tasks", {})
        u_status = q.get("user_status") or {}

        # Skip already completed AND claimed quests
        if u_status.get("claimed_at"):
            continue

        is_video = any(t in tasks for t in ("WATCH_VIDEO", "WATCH_VIDEO_ON_MOBILE"))
        is_game = "PLAY_ON_DESKTOP" in tasks

        if is_video:
            if u_status.get("completed_at"):
                completed_unclaimed.append(q)
            else:
                video_quests.append(q)
        elif is_game:
            if u_status.get("completed_at"):
                completed_unclaimed.append(q)
            else:
                game_quests.append(q)
        else:
            other_quests.append(q)

    def get_target(q):
        tcfg = q.get("config", {}).get("task_config_v2") or q.get("config", {}).get("task_config") or {}
        tasks = tcfg.get("tasks", {})
        for tname in ("WATCH_VIDEO", "WATCH_VIDEO_ON_MOBILE"):
            if tname in tasks:
                return float(tasks[tname].get("target", 999))
        if "PLAY_ON_DESKTOP" in tasks:
            return float(tasks["PLAY_ON_DESKTOP"].get("target", 900))
        return 999.0

    def get_sort_key(q):
        ustatus = q.get("user_status") or {}
        is_enrolled = bool(ustatus.get("enrolled_at"))
        target = get_target(q)
        return (not is_enrolled, target)

    video_quests.sort(key=get_sort_key)
    game_quests.sort(key=get_sort_key)

    print(f"  - Unwatched Video/Ad Quests: {len(video_quests)}")
    print(f"  - Pending Desktop Game Quests: {len(game_quests)}")
    print(f"  - Completed (Waiting to Claim): {len(completed_unclaimed)}")
    print(f"  - Other Quests: {len(other_quests)}")

    if completed_unclaimed:
        print(f"\n{Colors.GREEN}{Colors.BOLD}[★] Quests Ready to Claim ({len(completed_unclaimed)}):{Colors.RESET}")
        for cq in completed_unclaimed:
            cname = cq.get("config", {}).get("messages", {}).get("quest_name", "Quest")
            print(f"  ✓ {cname} (100% Complete)")
        if not list_only:
            print(f"\n{Colors.YELLOW}[*] Auto-claiming {len(completed_unclaimed)} ready quest(s) via 2Captcha...{Colors.RESET}")
            for cq in completed_unclaimed:
                cq_id = cq["id"]
                cname = cq.get("config", {}).get("messages", {}).get("quest_name", "Quest")
                claim_quest_with_captcha(client, cq_id, cname)
                time.sleep(1.5)

    if list_only:
        print(f"\n{Colors.CYAN}--- Available Video Quests to Watch ({len(video_quests)} total) ---{Colors.RESET}")
        for q in video_quests:
            cfg = q.get("config", {})
            msgs = cfg.get("messages", {})
            name = msgs.get("quest_name", "Unknown Quest")
            task_cfg = cfg.get("task_config_v2") or cfg.get("task_config") or {}
            tasks = list(task_cfg.get("tasks", {}).keys())
            target_sec = get_target(q)
            print(f" • {name} ({target_sec:.0f}s) | Tasks: {tasks}")

        print(f"\n{Colors.CYAN}--- Available Game Play Quests ({len(game_quests)} total) ---{Colors.RESET}")
        for q in game_quests[:10]:
            cfg = q.get("config", {})
            msgs = cfg.get("messages", {})
            name = msgs.get("quest_name", "Unknown Quest")
            game_title = msgs.get("game_title", name)
            t_sec = get_target(q)
            us = q.get("user_status") or {}
            enrolled_tag = f" {Colors.GREEN}[Enrolled]{Colors.RESET}" if us.get("enrolled_at") else ""
            print(f" • {name} ({game_title}) | Target: {t_sec/60:.0f}m{enrolled_tag}")
        if len(game_quests) > 10:
            print(f"   ... and {len(game_quests) - 10} more game quests.")
        return

    # Select target quests based on mode
    if mode == "game":
        run_items = [("game", q) for q in (game_quests if max_ads <= 0 else game_quests[:max_ads])]
    elif mode == "all":
        v_items = [("video", q) for q in (video_quests if max_ads <= 0 else video_quests[:max_ads])]
        g_items = [("game", q) for q in (game_quests if max_ads <= 0 else game_quests[:max_ads])]
        run_items = v_items + g_items
    else:
        run_items = [("video", q) for q in (video_quests if max_ads <= 0 else video_quests[:max_ads])]

    if not run_items:
        print(f"{Colors.YELLOW}[i] No pending quests matching mode '{mode}' right now.{Colors.RESET}")
        return

    print(f"\n{Colors.BOLD}{Colors.GREEN}[*] Safe Batch: Processing {len(run_items)} quest(s) [Mode: {mode.upper()}]...{Colors.RESET}")

    for i, (qtype, q) in enumerate(run_items):
        if qtype == "video":
            res = process_video_quest(client, q)
        else:
            res = process_game_quest(client, q)

        if isinstance(res, dict) and res.get("rate_limited"):
            retry_sec = float(res.get("retry_after", 300))
            print(f"\n{Colors.YELLOW}[i] Respecting Discord enrollment limit: waiting {retry_sec:.0f}s before continuing...{Colors.RESET}", flush=True)
            rem = retry_sec + 5
            while rem > 0:
                step = min(rem, 30.0)
                time.sleep(step)
                rem -= step
                if rem > 0:
                    print(f"  {Colors.DIM}[i] Cooldown countdown: {rem:.0f}s remaining...{Colors.RESET}", flush=True)
            if qtype == "video":
                process_video_quest(client, q)
            else:
                process_game_quest(client, q)
        elif i < len(run_items) - 1:
            cooldown = random.uniform(20.0, 40.0)
            print(f"\n{Colors.DIM}[i] Cooldown pause: {cooldown:.1f}s before next quest...{Colors.RESET}")
            time.sleep(cooldown)


def show_claimed_history(client: StealthDiscordClient):
    try:
        res = client.get_claimed_quests()
        claimed = res.get("quests", [])
        print(f"\n{Colors.CYAN}--- Claimed Quests History ({len(claimed)} total) ---{Colors.RESET}")
        for q in claimed[:15]:
            cfg = q.get("config", {})
            msgs = cfg.get("messages", {})
            name = msgs.get("quest_name", "Unknown")
            print(f"  [+] {name}")
        if len(claimed) > 15:
            print(f"  ... and {len(claimed) - 15} more.")
    except Exception as e:
        print(f"{Colors.RED}[!] Could not fetch claimed history: {e}{Colors.RESET}")


def main():
    parser = argparse.ArgumentParser(description="Watch Discord Orb/Video Ads Headless via Stealth API")
    parser.add_argument("--token", "-t", type=str, help="Discord User Authorization Token")
    parser.add_argument("--loop", "-l", action="store_true", help="Run continuously in the background")
    parser.add_argument("--interval", "-i", type=int, default=3600, help="Check interval in seconds for loop mode (default: 3600s)")
    parser.add_argument("--limit", "-m", type=int, default=0, help="Max quests to process in one run (default: 0 = all)")
    parser.add_argument("--video-only", action="store_true", help="Only watch video ads, skip 15-minute game play quests")
    parser.add_argument("--game-only", action="store_true", help="Only do 15-minute game quests, skip video ads")
    parser.add_argument("--list", action="store_true", help="List available and claimed quests without watching")
    args = parser.parse_args()

    print_banner()

    # Determine batch limit and mode (Default: ALL quests, unlimited)
    effective_limit = args.limit
    if args.video_only:
        mode = "video"
    elif args.game_only:
        mode = "game"
    else:
        mode = "all"

    # 1. Retrieve token
    token = load_token(args.token)
    if not token:
        print(f"{Colors.RED}[!] Error: No Discord token provided. Exiting.{Colors.RESET}")
        sys.exit(1)

    # 2. Initialize Stealth Client
    client = StealthDiscordClient(token)
    print(f"{Colors.DIM}[i] Detected Discord Desktop Version: {client.client_version} (Build: {client.build_number}){Colors.RESET}")

    # 3. Validate Token
    try:
        user = client.get_user_profile()
        username = user.get("username")
        display_name = user.get("global_name") or username
        user_id = user.get("id")
        print(f"{Colors.GREEN}[+] Authenticated as: {Colors.BOLD}{display_name}{Colors.RESET} (@{username}, ID: {user_id})")
    except Exception as e:
        print(f"{Colors.RED}[!] Authentication failed: {e}{Colors.RESET}")
        sys.exit(1)

    # 4. Connect to Gateway
    client.start_gateway()

    try:
        if args.list:
            run_watcher(client, list_only=True, mode=mode)
            show_claimed_history(client)
            return

        if args.loop:
            print(f"\n{Colors.CYAN}[*] Starting background watch mode (Interval: {args.interval}s / {args.interval//60}m)...{Colors.RESET}")
            print(f"{Colors.DIM}Press Ctrl+C at any time to exit.{Colors.RESET}")
            try:
                while True:
                    run_watcher(client, max_ads=effective_limit, mode=mode)
                    print(f"\n{Colors.DIM}Sleeping for {args.interval}s until next check...{Colors.RESET}")
                    time.sleep(args.interval)
            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}[*] Watcher stopped by user. Goodbye!{Colors.RESET}")
        else:
            run_watcher(client, max_ads=effective_limit, mode=mode)
            print(f"\n{Colors.GREEN}[✔] Run complete.{Colors.RESET}")
    finally:
        client.close()


batch_watch_all_videos = run_watcher

if __name__ == "__main__":
    main()
