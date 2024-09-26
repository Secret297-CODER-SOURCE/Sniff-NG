import curses
import time
from arp_spoof import arp_spoof_attack, restore_arp
from network_scanner import scan_network
from dependency_manager import install_dependencies, enable_ip_forwarding, disable_ip_forwarding, setup_iptables, clear_iptables

# ASCII logo "Sniff-NG"
logo_art = [
    "",
    "",
    "",
    " ░▒▓███████▓▒░▒▓███████▓▒░░▒▓█▓▒░▒▓████████▓▒░▒▓████████▓▒░           ▒▓███████▓▒░ ░▒▓██████▓▒░  ",
    "░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░                 ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ ",
    "░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░                 ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░        ",
    " ░▒▓██████▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓██████▓▒░ ░▒▓██████▓▒░  ░▒▓███▓▒░ ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒▒▓███▓▒░ ",
    "       ░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░                 ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ ",
    "       ░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░                 ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ ",
    "░▒▓███████▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░                 ░▒▓█▓▒░░▒▓█▓▒░░▒▓██████▓▒░  ",
    ""
]

def draw_bordered_window(stdscr, y, x, height, width):
    """ Draw a bordered window at specified position with given dimensions. """
    stdscr.attron(curses.color_pair(6))
    stdscr.border(0)
    stdscr.attroff(curses.color_pair(6))

def draw_logo_and_menu(stdscr, current_row, menu):
    """ Draw the logo and menu on the screen with enhanced styling. """
    stdscr.clear()

    # Draw the logo
    for i, line in enumerate(logo_art):
        stdscr.addstr(i, 0, line, curses.color_pair(1))

    # Draw the menu
    draw_bordered_window(stdscr, len(logo_art) + 1, 0, 10, 50)
    stdscr.addstr(len(logo_art) + 2, 2, "=== Sniff-NG Menu ===", curses.A_BOLD | curses.color_pair(2))
    stdscr.addstr(len(logo_art) + 4, 2, "Use arrow keys to navigate and Enter to select.\n", curses.A_BOLD | curses.color_pair(3))

    for idx, row in enumerate(menu):
        y_position = len(logo_art) + 6 + idx
        if idx == current_row:
            stdscr.attron(curses.color_pair(4))
            stdscr.addstr(y_position, 2, f"> {row}")
            stdscr.attroff(curses.color_pair(4))
        else:
            stdscr.addstr(y_position, 4, row, curses.color_pair(5))
    stdscr.refresh()

def draw_status_bar(stdscr, message):
    """ Draw a status bar at the bottom of the screen. """
    height, width = stdscr.getmaxyx()
    stdscr.attron(curses.color_pair(7))
    stdscr.addstr(height - 1, 0, " " * (width - 1))  # Clear previous status
    stdscr.addstr(height - 1, 0, message)
    stdscr.attroff(curses.color_pair(7))
    stdscr.refresh()

def main_menu(stdscr):
    curses.curs_set(0)
    stdscr.clear()
    stdscr.refresh()

    # Color pairs
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)    # Logo color
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Menu title color
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)   # Instruction color
    curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)    # Highlighted menu item
    curses.init_pair(5, curses.COLOR_BLUE, curses.COLOR_BLACK)     # Normal menu item
    curses.init_pair(6, curses.COLOR_MAGENTA, curses.COLOR_BLACK)   # Border color
    curses.init_pair(7, curses.COLOR_BLACK, curses.COLOR_WHITE)     # Status bar color

    current_row = 0
    menu = ["Scan Network", "Start ARP Spoofing", "Restore ARP Tables", "Install Dependencies", "Exit"]

    while True:
        draw_logo_and_menu(stdscr, current_row, menu)
        draw_status_bar(stdscr, "Status: Ready | Use arrow keys to navigate | Press Enter to select.")

        key = stdscr.getch()

        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(menu) - 1:
            current_row += 1
        elif key in [curses.KEY_ENTER, 10, 13]:
            if current_row == 0:
                scan_network_ui(stdscr)
            elif current_row == 1:
                arp_spoofing_ui(stdscr)
            elif current_row == 2:
                restore_arp_ui(stdscr)
            elif current_row == 3:
                install_dependencies_ui(stdscr)
            elif current_row == 4:
                break


def scan_network_ui(stdscr):
    stdscr.clear()
    # Стартовая строка для вывода текста
    current_line = 2
    # Заголовок
    stdscr.addstr(current_line, 2, "=== Scanning Network ===", curses.A_BOLD | curses.color_pair(2))
    current_line += 2  # Переходим на 2 строки вниз
    # Информация о сканировании
    stdscr.addstr(current_line, 4, "Scanning Network...", curses.color_pair(3))
    stdscr.refresh()
    current_line += 2
    # Выполняем сканирование сети (функция должна быть определена отдельно)
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
    stdscr.addstr(current_line +2 , 2, "Press any key to return to main menu...", curses.color_pair(4))
    stdscr.getch()


def arp_spoofing_ui(stdscr):
    stdscr.clear()
    stdscr.addstr(2, 2, "=== ARP Spoofing ===", curses.A_BOLD | curses.color_pair(2))

    stdscr.addstr(4, 2, "Enter Target IP: ", curses.color_pair(3))
    curses.echo()
    target_ip = stdscr.getstr(4, 19, 15).decode("utf-8").strip()

    stdscr.addstr(5, 2, "Enter Gateway IP: ", curses.color_pair(3))
    gateway_ip = stdscr.getstr(5, 19, 15).decode("utf-8").strip()

    stdscr.clear()
    stdscr.addstr(2, 2, f"Starting ARP spoofing for target {target_ip} and gateway {gateway_ip}...", curses.color_pair(3))
    stdscr.refresh()

    enable_ip_forwarding()
    setup_iptables()

    try:
        arp_spoof_attack(target_ip, gateway_ip)
        stdscr.addstr(4, 2, "ARP spoofing in progress...", curses.color_pair(1))
    except Exception as e:
        stdscr.addstr(4, 2, f"Error: {str(e)}", curses.color_pair(5))
    finally:
        restore_arp(target_ip, gateway_ip)
        restore_arp(gateway_ip, target_ip)
        disable_ip_forwarding()
        clear_iptables()

    stdscr.addstr(6, 2, "Press any key to return to main menu...", curses.color_pair(4))
    stdscr.getch()

def restore_arp_ui(stdscr):
    stdscr.clear()
    stdscr.addstr(2, 2, "=== Restore ARP Tables ===", curses.A_BOLD | curses.color_pair(2))

    stdscr.addstr(4, 2, "Enter Target IP: ", curses.color_pair(3))
    curses.echo()
    target_ip = stdscr.getstr(4, 19, 15).decode("utf-8").strip()

    stdscr.addstr(5, 2, "Enter Gateway IP: ", curses.color_pair(3))
    gateway_ip = stdscr.getstr(5, 19, 15).decode("utf-8").strip()

    stdscr.clear()
    stdscr.addstr(2, 2, f"Restoring ARP tables for target {target_ip} and gateway {gateway_ip}...", curses.color_pair(3))
    stdscr.refresh()

    restore_arp(target_ip, gateway_ip)
    restore_arp(gateway_ip, target_ip)

    stdscr.addstr(4, 2, "ARP tables restored.", curses.color_pair(1))
    stdscr.addstr(6, 2, "Press any key to return to main menu...", curses.color_pair(4))
    stdscr.getch()

def install_dependencies_ui(stdscr):
    stdscr.clear()
    stdscr.addstr(2, 2, "=== Installing Dependencies ===", curses.A_BOLD | curses.color_pair(2))
    stdscr.addstr(4, 2, "Installing dependencies...", curses.color_pair(3))
    stdscr.refresh()

    install_dependencies()

    stdscr.addstr(6, 2, "Dependencies installed.", curses.color_pair(1))
    stdscr.addstr(8, 2, "Press any key to return to main menu...", curses.color_pair(4))
    stdscr.getch()

if __name__ == "__main__":
    curses.wrapper(main_menu)
