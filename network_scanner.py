import subprocess
from scapy.all import ARP, Ether, srp

def get_mac(ip):
    arp_request = ARP(pdst=ip)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered_list = srp(arp_request_broadcast, timeout=5, verbose=False)[0]
    return answered_list[0][1].hwsrc if answered_list else None

def scan_network():
    print("[*] Scanning the network...")
    try:
        scan_result = subprocess.check_output(["sudo", "arp-scan", "-l"], universal_newlines=True)
        print("[*] Scan results:")
        print(scan_result)

        devices = []
        lines = scan_result.strip().split("\n")[2:-4]  # Skip headers
        for line in lines:
            parts = line.split()
            ip, mac = parts[0], parts[1]
            devices.append({'ip': ip, 'mac': mac})

        return devices
    except subprocess.CalledProcessError as e:
        print(f"[!] Network scan error: {e}")
        return []
