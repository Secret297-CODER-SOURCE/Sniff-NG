import curses
import subprocess
from scapy.all import ARP, Ether, srp


# Функция для получения MAC-адреса
def get_mac(ip):
    arp_request = ARP(pdst=ip)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered_list = srp(arp_request_broadcast, timeout=5, verbose=False)[0]
    return answered_list[0][1].hwsrc if answered_list else None


# Функция для сканирования сети
def scan_network():
    try:
        scan_result = subprocess.check_output(["sudo", "arp-scan", "-l"], universal_newlines=True)

        devices = []
        lines = scan_result.strip().split("\n")[2:-4]  # Пропускаем заголовки
        for line in lines:
            parts = line.split()
            ip, mac = parts[0], parts[1]
            devices.append({'ip': ip, 'mac': mac})

        return devices
    except subprocess.CalledProcessError as e:
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
