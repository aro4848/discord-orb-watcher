"""
Discord Quest & Orb Auto-Completer Module
=========================================
Integrated quest watcher for Discord ID Scraper / Raider Pro suite.
Automates video and gaming quests for Orbs, avatar decorations, and rewards.
"""

import os
import sys
import json
import time
import traceback
from colorama import Fore, Style, init

try:
    import wcwidth
except ImportError:
    wcwidth = None

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    os.system("")

init(autoreset=True)

CONFIG_FILE = "config.json"

DRAGON_LINES = [
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀",
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⣴⣶⣿⣿⣶⣶⣶⣶⣦⣤⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀",
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⠶⠿⠿⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣦⣀⠀⠀⠀⠀⠀⠀⠀⠀",
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡄⢀⠴⠀⠀⠀⠀⠀⠀⠀⠈⠙⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣄⠀⠀⠀⠀⠀⠀",
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣎⣴⣋⣠⣤⣔⣠⣤⣤⣠⣀⣀⠀⠀⠈⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣄⠀⠀⠀⠀",
    "⠀⠀⠀⠀⠀⠀⠀⠀⣠⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⣂⠈⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⡀⠀⠀",
    "⠀⠀⠀⠀⠀⠀⢠⡾⣻⣿⣿⣿⣿⠿⠿⠿⠿⢿⣿⣿⣿⣿⣿⣿⣿⣷⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⣿⣧⡀⠀",
    "⠀⠀⠀⠀⠀⣀⣾⣿⣿⣿⠿⠛⠂⠀⠀⡀⠀⠀⠈⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡈⢻⣿⣿⣆⠈⢻⣧⠀",
    "⠀⠀⠀⠀⠻⣿⠛⠉⠀⠀⠀⠀⢀⣤⣾⣿⣦⣤⣤⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣄⠙⢿⣿⣿⣿⡇⠀⢻⣿⣿⡀⠀⠻⡆",
    "⠀⠀⣰⣤⣤⣤⣤⣤⣤⣴⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⠈⢻⣿⣿⣿⠀⠀⢹⣿⣇⠀⠀⠳",
    "⠀⢰⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⠛⢻⠛⠛⠻⣿⣿⣿⣿⣿⣿⣿⣧⠀⢻⣿⣿⡆⠀⠀⢻⣿⠀⠀⠀",
    "⠀⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⠁⠀⠼⠛⢿⣶⣦⣿⣿⠻⣿⣿⣿⣿⣿⣇⠀⢻⣿⡇⠀⠀⠀⣿⠀⠀⠀",
    "⠸⠛⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣟⠀⠀⠀⠀⠀⠘⠁⠈⠛⠋⠀⠘⢿⣿⣿⣿⣿⡀⠈⣿⡇⠀⠀⠀⢸⡇⠀⠀",
    "⠀⠈⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣿⣿⣿⣿⡇⠀⹇⠀⠀⠀⠈⠀⠀⠀",
    "⠀⠀⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⡇⠀⠼⠀⠀⠀⠀⠀⠀⠀⠀",
    "⠀⠀⠘⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⡉⠛⠛⠿⠿⣦⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢈⣿⣿⣿⠁aro22 on dc",
    "⠀⠀⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⡀⠀⠀⠀⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⡏",
    "⠀⠀⠀⠀⠘⢿⣿⣿⣿⣷⡀⠉⠙⠻⠿⢿⣿⣷⣤⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣾⣿⡟⠀⠀",
    "⠀⠀⠀⠀⠀⠈⠻⣿⣿⣿⣷⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⣿⠏",
    "⠀⠀⠀⠀⠀⠀⠀⠀⠙⠿⣿⣿⣦⡀⠀⠀⠀⠀⠀⠀⠀⢀⡄⠀⠀⠀⢀⣠⣾⠟⠁",
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠛⠿⢦⣀⠀⠀⠀⢀⣴⣿⣧⣤⣴⣾⡿⠛⠁",
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⠛⠛⠛⠛⠛⠉⠁"
]

MENU_LINES = [
    f"{Fore.RED}╔══════════════════════════════════════════════════════════╗",
    f"{Fore.RED}║         {Fore.YELLOW}Discord Quest & Orb Auto-Completer{Fore.RED}               ║",
    f"{Fore.RED}╠══════════════════════════════════════════════════════════╣",
    f"{Fore.RED}║ {Fore.CYAN}[1] {Fore.WHITE}Auto-Complete All Video/Ad Quests (Orbs)          {Fore.RED}║",
    f"{Fore.RED}║ {Fore.CYAN}[2] {Fore.WHITE}Auto-Complete Desktop Game Quests (Play Quests)   {Fore.RED}║",
    f"{Fore.RED}║ {Fore.CYAN}[3] {Fore.WHITE}Complete All Active Quests (Video + Game)         {Fore.RED}║",
    f"{Fore.RED}║ {Fore.CYAN}[4] {Fore.WHITE}List All Active & Pending Quests                  {Fore.RED}║",
    f"{Fore.RED}║ {Fore.CYAN}[5] {Fore.WHITE}View Claimed Quest History                        {Fore.RED}║",
    f"{Fore.RED}║ {Fore.CYAN}[6] {Fore.WHITE}Back to Main Menu                                 {Fore.RED}║",
    f"{Fore.RED}╚══════════════════════════════════════════════════════════╝"
]

CHOICE_MAP = {
    "1": "Auto-Complete All Video/Ad Quests (Orbs)",
    "2": "Auto-Complete Desktop Game Quests (Play Quests)",
    "3": "Complete All Active Quests (Video + Game)",
    "4": "List All Active & Pending Quests",
    "5": "View Claimed Quest History"
}

class SideBySideOutput:
    """Redirects stdout/stderr so the Dragon ASCII stays on the left and logs stream on the right."""
    def __init__(self, original_stdout, dragon_lines, col_w=48):
        self.original_stdout = original_stdout
        self.dragon_lines = dragon_lines
        self.col_w = col_w
        self.current_line = 0
        self.line_buf = ""
        self.encoding = getattr(original_stdout, "encoding", "utf-8")
        self.errors = getattr(original_stdout, "errors", "replace")

    def _get_left_prefix(self, line_idx):
        if line_idx < len(self.dragon_lines):
            dl = self.dragon_lines[line_idx]
            try:
                dw = wcwidth.wcswidth(dl) if wcwidth else len(dl)
            except Exception:
                dw = len(dl)
            pad = max(0, self.col_w - dw)
            return Fore.RED + dl + (" " * pad) + Fore.RESET + "  "
        else:
            return (" " * self.col_w) + "  "

    def write(self, s):
        if not s:
            return
        if s.startswith("\r"):
            content = s[1:]
            prefix = self._get_left_prefix(self.current_line)
            self.original_stdout.write("\r" + prefix + content + "\033[K")
            self.original_stdout.flush()
            return

        self.line_buf += s
        while "\n" in self.line_buf:
            line, self.line_buf = self.line_buf.split("\n", 1)
            prefix = self._get_left_prefix(self.current_line)
            self.original_stdout.write(prefix + line + "\n")
            self.current_line += 1
            self.original_stdout.flush()

    def flush(self):
        if self.line_buf:
            prefix = self._get_left_prefix(self.current_line)
            self.original_stdout.write(prefix + self.line_buf + "\n")
            self.current_line += 1
            self.line_buf = ""
        self.original_stdout.flush()

    def finish_dragon(self):
        self.flush()
        while self.current_line < len(self.dragon_lines):
            prefix = self._get_left_prefix(self.current_line)
            self.original_stdout.write(prefix + "\n")
            self.current_line += 1
        self.original_stdout.flush()

    def isatty(self):
        return getattr(self.original_stdout, "isatty", lambda: False)()

    def fileno(self):
        return self.original_stdout.fileno()


def render_side_by_side():
    """Renders the Dragon ASCII art on the left and Quest menu on the right."""
    col_w = 48
    start_row = 3
    total_rows = max(len(DRAGON_LINES), start_row + len(MENU_LINES))

    for r in range(total_rows):
        if r < len(DRAGON_LINES):
            dl = DRAGON_LINES[r]
            try:
                dw = wcwidth.wcswidth(dl) if wcwidth else len(dl)
            except Exception:
                dw = len(dl)
            pad = max(0, col_w - dw)
            left = Fore.RED + dl + (" " * pad)
        else:
            left = " " * col_w

        mid = "  "
        menu_r = r - start_row
        if 0 <= menu_r < len(MENU_LINES):
            right = MENU_LINES[menu_r]
        else:
            right = ""

        print(left + mid + right)

def load_config():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    cfg_path = os.path.join(base_dir, CONFIG_FILE)
    if os.path.exists(cfg_path):
        try:
            with open(cfg_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def get_working_token(dow):
    """Loads configured token or auto-detects active token from Discord desktop."""
    config = load_config()
    token = config.get("user_token") or config.get("token")
    if token:
        try:
            c = dow.StealthDiscordClient(token)
            r = c.session.get("https://discord.com/api/v9/users/@me")
            if r.status_code == 200:
                u = r.json()
                print(f"{Fore.GREEN}[+] Active session: {Fore.WHITE}{u.get('username')} ({u.get('id')}){Fore.RESET}")
                return token
            else:
                print(f"{Fore.YELLOW}[!] Configured token is expired (HTTP {r.status_code}). Auto-detecting live session...{Fore.RESET}")
        except Exception:
            pass

    print(f"{Fore.CYAN}[*] Scanning local Discord desktop for active session...{Fore.RESET}")
    try:
        tokens = dow.find_discord_tokens()
        for tok in tokens:
            try:
                c = dow.StealthDiscordClient(tok)
                r = c.session.get("https://discord.com/api/v9/users/@me")
                if r.status_code == 200:
                    u = r.json()
                    print(f"{Fore.GREEN}[+] Found valid session for {Fore.WHITE}{u.get('username')}{Fore.RESET}")
                    # Save back to config.json
                    base_dir = os.path.dirname(os.path.abspath(__file__))
                    cfg_path = os.path.join(base_dir, CONFIG_FILE)
                    try:
                        with open(cfg_path, "r", encoding="utf-8") as f:
                            cfg_data = json.load(f)
                        cfg_data["token"] = tok
                        cfg_data["user_token"] = tok
                        with open(cfg_path, "w", encoding="utf-8") as f:
                            json.dump(cfg_data, f, indent=4)
                    except Exception:
                        pass
                    return tok
            except Exception:
                continue
    except Exception as e:
        print(f"{Fore.RED}[!] Auto-detection error: {e}{Fore.RESET}")

    token = input(f"\n{Fore.YELLOW}Enter your Discord user token: {Fore.WHITE}").strip()
    return token

def run_quest_watcher(update_status_func=None):
    if update_status_func:
        update_status_func(f"{Fore.CYAN}Discord Quest & Orb Watcher")

    while True:
        # Clear screen and show side-by-side menu
        os.system("cls" if os.name == "nt" else "clear")
        render_side_by_side()

        raw_choice = input(f"\n{Fore.YELLOW}Enter your choice (1-6): {Fore.WHITE}")
        choice = "".join(c for c in raw_choice if c.isdigit()).strip()
        if choice == "6" or not choice:
            return

        selected_label = CHOICE_MAP.get(choice, f"Option [{choice}]")

        # Clear screen completely so the menu gets replaced with logs, while the DRAGON STAYS
        os.system("cls" if os.name == "nt" else "clear")

        # Direct stdout and stderr to SideBySideOutput so dragon stays on left and logs stream on right
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        side_writer = SideBySideOutput(old_stdout, DRAGON_LINES, col_w=48)
        sys.stdout = side_writer
        sys.stderr = side_writer

        try:
            # Print breadcrumb header with > > > indicator on the right side next to Dragon
            print(f"{Fore.CYAN}Raider Pro {Fore.YELLOW}> {Fore.CYAN}Quest Watcher {Fore.YELLOW}> {Fore.GREEN}{selected_label}{Fore.RESET}")
            print(f"{Fore.YELLOW}>>> Selected: {Fore.WHITE}{selected_label}{Fore.RESET}")
            print(f"{Fore.RED}──────────────────────────────────────────────────────────────────{Fore.RESET}\n")

            # Locate discord_orb_watcher
            orb_script_path = None
            candidate_paths = [
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "discord_orb_watcher.py"),
                r"C:\Users\PC\Downloads\cradleKoi-main\cradleKoi-main\discord_orb_watcher.py",
                r"C:\Users\PC\Desktop\discord_orb_watcher.py"
            ]
            for p in candidate_paths:
                if os.path.exists(p):
                    orb_script_path = p
                    break

            if not orb_script_path:
                print(f"{Fore.RED}[!] Could not locate discord_orb_watcher.py engine.{Fore.RESET}")
                continue

            # Add directory to sys.path to import dynamically
            engine_dir = os.path.dirname(orb_script_path)
            if engine_dir not in sys.path:
                sys.path.insert(0, engine_dir)

            try:
                import discord_orb_watcher as dow
            except Exception as e:
                print(f"{Fore.RED}[!] Error loading quest engine: {e}{Fore.RESET}")
                continue

            token = get_working_token(dow)
            if not token:
                print(f"{Fore.RED}[!] No valid token available. Aborting.{Fore.RESET}")
                continue

            print(f"{Fore.CYAN}[*] Initializing stealth client & inspecting quests...{Fore.RESET}")
            client = None
            try:
                client = dow.StealthDiscordClient(token)
                client.start_gateway()

                if choice == "1":
                    print(f"{Fore.GREEN}[*] Starting Video/Ad Quest Watcher...{Fore.RESET}")
                    dow.run_watcher(client, max_ads=0, mode="video", list_only=False)
                elif choice == "2":
                    print(f"{Fore.GREEN}[*] Starting Desktop Game Quest Simulator...{Fore.RESET}")
                    dow.run_watcher(client, max_ads=0, mode="game", list_only=False)
                elif choice == "3":
                    print(f"{Fore.GREEN}[*] Processing All Active Quests...{Fore.RESET}")
                    dow.run_watcher(client, max_ads=0, mode="all", list_only=False)
                elif choice == "4":
                    dow.run_watcher(client, list_only=True)
                    dow.show_claimed_history(client)
                elif choice == "5":
                    dow.show_claimed_history(client)

            finally:
                if client:
                    try:
                        client.close()
                    except Exception:
                        pass

        except Exception as e:
            print(f"\n{Fore.RED}[!] Quest engine error: {e}{Fore.RESET}")
            traceback.print_exc()
        finally:
            side_writer.finish_dragon()
            sys.stdout = old_stdout
            sys.stderr = old_stderr

        try:
            input(f"\n{Fore.YELLOW}Press Enter to return to menu...{Fore.WHITE}")
        except (EOFError, KeyboardInterrupt):
            break

if __name__ == "__main__":
    try:
        run_quest_watcher()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Exiting quest watcher...")
