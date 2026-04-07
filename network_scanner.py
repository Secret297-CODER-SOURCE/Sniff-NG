import curses
import subprocess
import ipaddress
import platform


# Функция для получения MAC-адреса
def get_mac(ip):
    from scapy.all import ARP, Ether, srp

    arp_request = ARP(pdst=ip)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered_list = srp(arp_request_broadcast, timeout=5, verbose=False)[0]
    return answered_list[0][1].hwsrc if answered_list else None


def detect_default_gateway():
    gateway_ip = _gateway_from_scapy()
    if gateway_ip:
        return gateway_ip

    system = platform.system().lower()
    if system == "linux":
        return _gateway_from_linux_route()
    if system == "darwin":
        return _gateway_from_macos_route()
    return None


def _gateway_from_scapy():
    try:
        from scapy.all import conf

        route = conf.route.route("0.0.0.0")
        gateway_ip = route[2] if len(route) > 2 else None
        return _validated_ipv4(gateway_ip)
    except Exception:
        return None


def _gateway_from_linux_route():
    try:
        output = subprocess.check_output(["ip", "route", "show", "default"], text=True)
        for token in output.split():
            candidate = _validated_ipv4(token)
            if candidate:
                return candidate
    except Exception:
        return None
    return None


def _gateway_from_macos_route():
    try:
        output = subprocess.check_output(["route", "-n", "get", "default"], text=True)
        for line in output.splitlines():
            if "gateway:" in line:
                candidate = line.split(":", 1)[1].strip()
                return _validated_ipv4(candidate)
    except Exception:
        return None
    return None


def _validated_ipv4(value):
    if not value:
        return None
    try:
        return str(ipaddress.ip_address(value)) if ipaddress.ip_address(value).version == 4 else None
    except ValueError:
        return None


# Функция для сканирования сети
def scan_network():
    if _is_installed("arp-scan"):
        devices = _scan_with_arp_scan()
        if devices:
            return devices

    return _scan_with_scapy()


def _is_installed(program):
    return subprocess.run(["which", program], stdout=subprocess.PIPE, stderr=subprocess.PIPE).returncode == 0


def _scan_with_arp_scan():
    try:
        command = ["sudo", "arp-scan", "-l"]
        if platform.system().lower() == "darwin":
            # macOS users usually scan the active interface explicitly.
            command = ["sudo", "arp-scan", "--interface=en0", "--localnet"]

        scan_result = subprocess.check_output(command, universal_newlines=True)

        devices = []
        lines = scan_result.strip().split("\n")[2:-4]  # Пропускаем заголовки
        for line in lines:
            parts = line.split()
            if len(parts) >= 2:
                ip, mac = parts[0], parts[1]
                devices.append({'ip': ip, 'mac': mac})

        return devices
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []


def _scan_with_scapy():
    try:
        from scapy.all import conf, ARP, Ether, srp

        _, local_ip, _ = conf.route.route("0.0.0.0")
        target_network = ipaddress.ip_network(f"{local_ip}/24", strict=False)
        request = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=str(target_network))
        answered = srp(request, timeout=2, verbose=False)[0]

        devices = []
        seen = set()
        for _, response in answered:
            key = (response.psrc, response.hwsrc)
            if key not in seen:
                seen.add(key)
                devices.append({'ip': response.psrc, 'mac': response.hwsrc})
        return devices
    except Exception:
        return []


# Интерфейс с использованием curses
def scan_network_ui(stdscr):
    stdscr.clear()

    # Стартовая строка для вывода текста
    current_line = 2

    # Заголовок
    stdscr.addstr(current_line, 2, "=== Scanning Network ===", curses.A_BOLD | curses.color_pair(2))
    current_line += 2  # Переходим на 2 строки вниз

    # Информация о сканировании
    stdscr.addstr(current_line, 2, "Scanning Network...", curses.color_pair(3))
    stdscr.refresh()

    # Выполняем сканирование сети
    devices = scan_network()

    current_line += 2  # Переходим на следующую строку для результатов

    # Если устройства не найдены
    if not devices:
        stdscr.addstr(current_line, 2, "No devices found.", curses.color_pair(5))
    else:
        # Выводим найденные устройства
        stdscr.addstr(current_line, 2, "Devices found:", curses.color_pair(3))
        current_line += 1  # Переходим на следующую строку
        for device in devices:
            stdscr.addstr(current_line, 4, f"IP: {device['ip']}, MAC: {device['mac']}", curses.color_pair(3))
            current_line += 1  # Переходим на следующую строку после каждого устройства

    # Сообщение о возвращении в главное меню
    stdscr.addstr(current_line + 2, 2, "Press any key to return to main menu...", curses.color_pair(4))
    stdscr.getch()


# Основная функция запуска TUI
def main():
    curses.wrapper(scan_network_ui)


if __name__ == "__main__":
    main()
