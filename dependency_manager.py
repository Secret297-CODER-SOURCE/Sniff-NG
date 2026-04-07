import os
import subprocess
import platform
import sys

def is_installed(program):
    return subprocess.run(["which", program], stdout=subprocess.PIPE, stderr=subprocess.PIPE).returncode == 0


def get_platform():
    return platform.system().lower()

def get_linux_distribution():
    if os.path.exists("/etc/os-release"):
        with open("/etc/os-release") as f:
            for line in f:
                if line.startswith("ID="):
                    return line.strip().split('=')[1].lower()
    return platform.system().lower()

def install_package(package_name):
    system = get_platform()

    if system == "linux":
        distro = get_linux_distribution()
        if distro in ['ubuntu', 'debian']:
            subprocess.run(["sudo", "apt-get", "install", "-y", package_name], check=True)
        elif distro in ['fedora', 'centos']:
            subprocess.run(["sudo", "dnf", "install", "-y", package_name], check=True)
        elif distro in ['arch', 'manjaro']:
            subprocess.run(["sudo", "pacman", "-Sy", "--noconfirm", package_name], check=True)
        else:
            print(f"[!] Unsupported Linux distribution: {distro}. Please install {package_name} manually.")
            return False
        return True

    if system == "darwin":
        if is_installed("brew"):
            subprocess.run(["brew", "install", package_name], check=True)
            return True
        print(f"[!] Homebrew is not installed. Please install {package_name} manually.")
        return False

    print(f"[!] Unsupported platform: {system}. Please install {package_name} manually.")
    return False


def install_python_package(package_name):
    subprocess.run([sys.executable, "-m", "pip", "install", package_name], check=True)

def install_dependencies():
    print("[*] Installing necessary packages...")
    system = get_platform()

    if not is_installed("arp-scan"):
        print("[*] Installing arp-scan...")
        try:
            install_package("arp-scan")
        except subprocess.CalledProcessError:
            print("[!] Failed to install arp-scan automatically.")
    else:
        print("[*] arp-scan is already installed.")

    if system == "linux":
        if not is_installed("dsniff"):
            print("[*] Installing dsniff...")
            try:
                install_package("dsniff")
            except subprocess.CalledProcessError:
                print("[!] Failed to install dsniff automatically.")
        else:
            print("[*] dsniff is already installed.")
    else:
        print("[*] dsniff install is skipped on macOS.")

    try:
        import scapy
    except ImportError:
        print("[*] Installing scapy...")
        try:
            install_package("scapy")
        except Exception:
            install_python_package("scapy")


    try:
        import mitmproxy
    except ImportError:
        print("[*] Installing mitmproxy...")
        install_python_package("mitmproxy")

    print("[*] All necessary packages installed.")

def enable_ip_forwarding():
    system = get_platform()
    if system == "linux":
        subprocess.run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    elif system == "darwin":
        subprocess.run(["sysctl", "-w", "net.inet.ip.forwarding=1"], check=False)
    else:
        print(f"[!] IP forwarding is not implemented for platform: {system}")

def disable_ip_forwarding():
    system = get_platform()
    if system == "linux":
        subprocess.run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    elif system == "darwin":
        subprocess.run(["sysctl", "-w", "net.inet.ip.forwarding=0"], check=False)
    else:
        print(f"[!] IP forwarding is not implemented for platform: {system}")

def setup_iptables():
    if get_platform() == "linux":
        os.system("iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8080")
        os.system("iptables -t nat -A PREROUTING -p tcp --dport 443 -j REDIRECT --to-port 8080")
        return True

    if get_platform() == "darwin":
        print("[!] iptables redirection is Linux-only. Configure pf manually on macOS if needed.")
        return False

    print(f"[!] Packet redirection is not implemented for platform: {get_platform()}")
    return False

def forward_config():
    enable_ip_forwarding()


def clear_iptables():
    if get_platform() == "linux":
        os.system("iptables -t nat -D PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8080")
        os.system("iptables -t nat -D PREROUTING -p tcp --dport 443 -j REDIRECT --to-port 8080")
        return True

    if get_platform() == "darwin":
        print("[!] iptables cleanup is Linux-only. Clear pf rules manually on macOS if configured.")
        return False

    print(f"[!] Packet redirection cleanup is not implemented for platform: {get_platform()}")
    return False
