# discord-orb-watcher

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue)](https://www.python.org/)
[![Discord](https://img.shields.io/badge/Discord-aro22-7289DA)](https://discord.com/users/aro22)
[![GitHub Stars](https://img.shields.io/github/stars/aro4848/discord-orb-watcher?style=flat-square)](https://github.com/aro4848/discord-orb-watcher)

discord video ad & quest auto-completer. watch ads, finish quests, grab orbs, zero browser bloat.

most quest scripts out there are sketchy devtools console pastebins or client plugins that spam heartbeat endpoints with zero context. discord flags that in seconds because there is no gateway session, no genuine tls fingerprint, and no actual media traffic to their cdn.

discord-orb-watcher runs completely headless without having discord or any game running, while looking 100% legitimate to discord's backend.

```text
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⣴⣶⣿⣿⣶⣶⣶⣶⣦⣤⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⠶⠿⠿⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣦⣀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡄⢀⠴⠀⠀⠀⠀⠀⠀⠀⠈⠙⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣄⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣎⣴⣋⣠⣤⣔⣠⣤⣤⣠⣀⣀⠀⠀⠈⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣄⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⣠⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⣂⠈⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⡀⠀⠀
⠀⠀⠀⠀⠀⠀⢠⡾⣻⣿⣿⣿⣿⠿⠿⠿⠿⢿⣿⣿⣿⣿⣿⣿⣿⣷⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⣿⣧⡀⠀
⠀⠀⠀⠀⠀⣀⣾⣿⣿⣿⠿⠛⠂⠀⠀⡀⠀⠀⠈⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡈⢻⣿⣿⣆⠈⢻⣧⠀
⠀⠀⠀⠀⠻⣿⠛⠉⠀⠀⠀⠀⢀⣤⣾⣿⣦⣤⣤⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣄⠙⢿⣿⣿⣿⡇⠀⢻⣿⣿ ⠀⠻⡆
⠀⠀⣰⣤⣤⣤⣤⣤⣤⣴⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⠈⢻⣿⣿⣿⠀⠀⢹⣿⣇⠀⠀⠳
⠀⢰⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⠛⢻⠛⠛⠻⣿⣿⣿⣿⣿⣿⣿⣧⠀⢻⣿⣿⡆⠀⠀⢻⣿⠀⠀⠀
⠀⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⠁⠀⠼⠛⢿⣶⣦⣿⣿⠻⣿⣿⣿⣿⣿⣇⠀⢻⣿⡇⠀⠀⠀⣿⠀⠀⠀
⠸⠛⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣟⠀⠀⠀⠀⠀⠘⠁⠈⠛⠋⠀⠘⢿⣿⣿⣿⣿⡀⠈⣿⡇⠀⠀⠀⢸⡇⠀⠀
⠀⠈⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣿⣿⣿⣿⡇⠀⹇⠀⠀⠀⠈⠀⠀⠀
⠀⠀⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⡇⠀⠼⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠘⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⡉⠛⠛⠿⠿⣦⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢈⣿⣿⣿⠁aro22 on dc
⠀⠀⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⡀⠀⠀⠀⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⡏    [skibidi]- made by skibidi aro https://github.com/aro4848
⠀⠀⠀⠀⠘⢿⣿⣿⣿⣷⡀⠉⠙⠻⠿⢿⣿⣷⣤⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⾾⣿⡟      [discord]: https://discord.com/users/aro22 on discord
⠀⠀⠀⠀⠀⠈⠻⣿⣿⣿⣷⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⣿⠏      [Engine: Stealth Gateway v9 + Range Buffering]
⠀⠀⠀⠀⠀⠀⠀⠀⠙⠿⣿⣿⣦⡀⠀⠀⠀⠀⠀⠀⠀⢀⡄⠀⠀⠀⢀⣠⣾⠟⠁
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠛⠿⢦⣀⠀⠀⠀⢀⣴⣿⣧⣤⣴⣾⡿⠛⠁
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⠛⠛⠛⠛⠛⠉⠁
```

### how it works

- **browser tls fingerprint (ja3/ja4)**: uses `curl_cffi` to mimic genuine chromium / electron client handshakes and http/2 framing instead of raw python signatures.
- **live gateway heartbeat**: connects straight to `wss://gateway.discord.gg/?v=9&encoding=json`, identifies with desktop properties, and keeps heartbeats alive throughout the run.
- **real cdn range streaming**: doesn't just fake progress timestamps — it pulls concurrent media chunks from `cdn.discordapp.com` with authentic `Range: bytes=...` headers so cdn egress logs line up with your quest activity.
- **zero config token grabber**: auto-discovers and decrypts your active token straight from local discord desktop (dpapi + leveldb) on windows. no copying tokens around.
- **video ads & 15-min game quests**: handles video quests for orbs / avatar decorations / nitro credits as well as 15-minute game play quests.
- **natural playback physics**: applies randomized micro-jitter and fractional drift so progression pings never look like a metronome script.
- **auto claim**: automatically claims the reward badge/code/decoration once the progress bar hits 100%.

### setup

```bash
git clone https://github.com/aro4848/discord-orb-watcher.git
cd discord-orb-watcher
pip install -r requirements.txt
```

### run

```bash
# interactive dragon menu
python main.py

# or headless auto-complete all video/orb quests
python main.py --headless

# or complete all available quests (video ads + game quests)
python main.py --all

# or just list active quests and your current orb balance
python main.py --list
```

### config (optional)

if discord desktop is logged in on your windows pc, you don't even need a `config.json` — it detects your active session automatically.

if you run on linux/vps or want to specify a custom token, copy `config.example.json` to `config.json`:

```json
{
  "token": "YOUR_DISCORD_USER_TOKEN",
  "auto_claim": true,
  "simulate_cdn_buffer": true
}
```

### disclaimer

i (aro4848) dont give a fuck if something happens to ur account. selfbotting quests is against discord TOS, so dont cry if discord gets mad. use an alt if you're paranoid. if you need help msg me on discord: **aro22**
