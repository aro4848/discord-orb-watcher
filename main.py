#!/usr/bin/env python3
"""
Discord Orb & Video Ad Auto-Watcher (Entry Point)
=================================================
Automates Discord video ads and quest completions for Orbs headless with
browser TLS (JA3/JA4) fingerprinting & genuine CDN media buffering.

Supports both interactive terminal UI (with side-by-side Dragon ASCII art)
and headless automated execution for servers/cron jobs.
"""

import sys
import argparse
import os

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    os.system("")

def main():
    parser = argparse.ArgumentParser(description="Discord Orb & Quest Auto-Watcher")
    parser.add_argument("--token", "-t", type=str, help="Discord user token (optional, auto-detected if omitted)")
    parser.add_argument("--headless", action="store_true", help="Run without interactive menu (auto-completes all video/ad quests)")
    parser.add_argument("--all", action="store_true", help="Auto-complete both video ad and desktop game quests")
    parser.add_argument("--list", action="store_true", help="List all available & active quests and exit")
    parser.add_argument("--menu", action="store_true", help="Force interactive dragon ASCII menu")

    args = parser.parse_args()

    if args.headless or args.all or args.list:
        import discord_orb_watcher
        sys.argv = [sys.argv[0]]
        if args.token:
            sys.argv.extend(["--token", args.token])
        if args.all:
            sys.argv.append("--all")
        if args.list:
            sys.argv.append("--list")
        discord_orb_watcher.main()
    else:
        import quest_watcher
        quest_watcher.run_quest_watcher()

if __name__ == "__main__":
    main()
