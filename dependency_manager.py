import os
import subprocess
import platform

def is_installed(program):
    return subprocess.run(["which", program], stdout=subprocess.PIPE, stderr=subprocess.PIPE).returncode == 0

def get_linux_distribution():
    if os.path.exists("/etc/os-release"):
        with open("/etc/os-release") as f:
            for line in f:
                if line.startswith("ID="):
                    return line.strip().split('=')[1].lower()
    return platform.system().lower()

def install_package(package_name):
    distro = get_linux_distribution()

    if distro in ['ubuntu', 'debian']:
        subprocess.run(["sudo", "apt-get", "install", "-y", package_name], check=True)
    elif distro in ['fedora', 'centos']:
        subprocess.run(["sudo", "dnf", "install", "-y", package_name], check=True)
    elif distro in ['arch', 'manjaro']:
        subprocess.run(["sudo", "pacman", "-Sy", "--noconfirm", package_name], check=True)
    else:
        print(f"[!] Unsupported distribution: {distro}. Please install {package_name} manually.")

def install_dependencies():
    pip_flag = input("[?] Do you want to enable '--break-system-packages' flag [y/n]: ")

    if pip_flag in ["y", "n"]:
        pip_flag = pip_flag == "y"
    else:
        print("[!] Please enter 'y' or 'n'")

    print("[*] Installing necessary packages...")

    if not is_installed("arp-scan"):
        print("[*] Installing arp-scan...")
        install_package("arp-scan")
    else:
        print("[*] arp-scan is already installed.")

    if not is_installed("dsniff"):
        print("[*] Installing dsniff...")
        install_package("dsniff")
    else:
        print("[*] dsniff is already installed.")

    try:
        import scapy
    except ImportError:
        print("[*] Installing scapy...")
        try:
            install_package("scapy")
        except:
            if pip_flag == False:
                subprocess.run(["sudo","pip", "install", "scapy"], check=True)
            else:
                subprocess.run(["sudo","pip", "install", "scapy", "--break-system-packages"], check=True)


    try:
        import mitmproxy
    except ImportError:
        print("[*] Installing mitmproxy...")
        if pip_flag == False:
            subprocess.run(["sudo","pip", "install", "mitmproxy"], check=True)
        else:
            subprocess.run(["sudo","pip", "install", "mitmproxy", "--break-system-packages"], check=True)

    print("[*] All necessary packages installed.")

def enable_ip_forwarding():
    os.system("echo 1 > /proc/sys/net/ipv4/ip_forward")

def disable_ip_forwarding():
    os.system("echo 0 > /proc/sys/net/ipv4/ip_forward")

def setup_iptables():
    os.system("iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8080")
    os.system("iptables -t nat -A PREROUTING -p tcp --dport 443 -j REDIRECT --to-port 8080")

def forward_config():
    os.system("sysctl -w net.ipv4.ip_forward=1")
    os.system("sysctl -w net.ipv4.ip_forward=1 ")


def clear_iptables():
    os.system("iptables -t nat -D PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8080")
    os.system("iptables -t nat -D PREROUTING -p tcp --dport 443 -j REDIRECT --to-port 8080")
