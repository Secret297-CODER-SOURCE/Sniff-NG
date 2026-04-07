# Sniff-NG

> **Powerful Python tool for network scanning, ARP spoofing, and local network MITM attacks with TUI interface.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
![Platform: Linux+macOS](https://img.shields.io/badge/platform-Linux%20%2B%20macOS-yellow)
![Status: Active](https://img.shields.io/badge/status-active-brightgreen)
![img.png](img.png)
---

**Tags:**  
`network` `arp-spoofing` `mitm` `sniffer` `ethical-hacking` `pentest` `python` `security` `tui` `linux` `macos` `local-network` `network-scanner` `infosec` `hacking-tool`

---

## About

**Sniff-NG** is a Python tool for network security testing.  
It provides fast local network device scanning, ARP spoofing (MITM), and a fully interactive TUI menu.  
Supports Linux and macOS with automatic dependency installation paths.

---

## Features

- **TUI interface:** no command line needed
- **Network scanner:** find all devices in the local network
- **Auto gateway detection:** detects default router IP for faster setup
- **ARP spoofing / MITM:** easy attack launch via menu
- **Restore ARP tables:** clean up after attacks
- **One-click dependency install:** Linux package managers + Homebrew on macOS
- **Python 3.8+** compatible

---

## Requirements

- Linux (Debian, Ubuntu, Arch, Fedora, CentOS, etc.) or macOS
- Python 3.8+
- Tools: `arp-scan` (`dsniff` is Linux-focused)
- Python libraries: `scapy`, `mitmproxy`

---

## Installation

```bash
git clone https://github.com/Secret297-CODER-SOURCE/Sniff-NG.git
cd Sniff-NG
sudo python3 console_ui.py
```
> **Run with `sudo`!**  
> Most features require root privileges for network access.

If dependencies are missing, select "Install dependencies" in the TUI menu.

### macOS notes

- Install Homebrew first: https://brew.sh
- Run Sniff-NG with elevated privileges (`sudo`) for raw packet operations.
- On macOS, scanner can use `arp-scan` (if installed) or Scapy ARP fallback.
- Linux `iptables` redirect helpers are not used on macOS (`pf` must be configured manually if you need redirect/NAT rules).

---

## Usage

All features are available via the TUI menu:
- **Network Scan:** shows all connected devices
- **ARP Spoofing:** attack any target/gateway on your LAN
- **Restore ARP:** cleans up ARP tables
- **Install dependencies:** one-click setup

**Controls:**  
- Up/Down: navigate  
- Enter: select  
- Hints at the bottom


---

## Security Notice

- For **educational and authorized penetration testing only**!
- Do not use against networks you do not own or have explicit permission to test.

---

## Contributing

Pull requests are welcome!  
Please open issues for bugs, ideas, or feature requests.

