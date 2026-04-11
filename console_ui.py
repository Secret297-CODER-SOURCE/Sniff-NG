import curses
import curses.textpad
import ipaddress
import socket
import time
from collections import defaultdict

import netifaces

from arp_spoof import arp_spoof_attack, restore_arp
from network_scanner import scan_network, detect_default_gateway
from dependency_manager import (
    install_dependencies,
    enable_ip_forwarding,
    disable_ip_forwarding,
    setup_iptables,
    clear_iptables,
)
import proxy_server

# ASCII-логотип "Sniff-NG"
logo_art = [
    "",
    "",
    "",
    # ASCII-логотип
    " ░▒▓███████▓▒░▒▓███████▓▒░░▒▓█▓▒░▒▓████████▓▒░▒▓████████▓▒░           ▒▓███████▓▒░ ░▒▓██████▓▒░  ",
    "░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░                 ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ ",
    "░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░                 ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░        ",
    " ░▒▓██████▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓██████▓▒░ ░▒▓██████▓▒░  ░▒▓███▓▒░ ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒▒▓███▓▒░ ",
    "       ░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░                 ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ ",
    "       ░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░                 ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ ",
    "░▒▓███████▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░                 ░▒▓█▓▒░░▒▓█▓▒░░▒▓██████▓▒░  ",
]


# ---------------------------------------------------------------------------
# Утилиты рисования
# ---------------------------------------------------------------------------

def safe_addstr(stdscr, y, x, text, attr=0):
    """Safely draw text in curses without overflowing terminal bounds."""
    height, width = stdscr.getmaxyx()
    if y < 0 or y >= height or x < 0 or x >= width:
        return
    available = width - x - 1
    if available <= 0:
        return
    clipped = text[:available]
    try:
        stdscr.addstr(y, x, clipped, attr)
    except curses.error:
        pass


def draw_bordered_window(stdscr, y, x, height, width):
    """Рисуем окно с рамкой в заданной позиции с определенными размерами."""
    stdscr.attron(curses.color_pair(6))  # Устанавливаем цвет для рамки
    stdscr.border(0)  # Рисуем границу вокруг окна
    stdscr.attroff(curses.color_pair(6))  # Отключаем цвет


def draw_logo_and_menu(stdscr, current_row, menu):
    """Рисуем логотип и меню на экране с улучшенным стилем."""
    stdscr.clear()  # Очищаем экран

    for i, line in enumerate(logo_art):
        safe_addstr(stdscr, i, 0, line, curses.color_pair(1))

    draw_bordered_window(stdscr, len(logo_art) + 1, 0, 10, 50)
    safe_addstr(stdscr, len(logo_art) + 2, 2, "=== Sniff-NG Меню ===", curses.A_BOLD | curses.color_pair(2))
    safe_addstr(stdscr, len(logo_art) + 4, 4, "WER1XY", curses.A_BOLD | curses.color_pair(1))
    safe_addstr(stdscr, len(logo_art) + 6, 2, "Используйте стрелки для навигации и Enter для выбора.", curses.A_BOLD | curses.color_pair(3))

    for idx, row in enumerate(menu):
        y_position = len(logo_art) + 8 + idx
        if idx == current_row:
            stdscr.attron(curses.color_pair(4))
            safe_addstr(stdscr, y_position, 2, f"> {row}")
            stdscr.attroff(curses.color_pair(4))
        else:
            safe_addstr(stdscr, y_position, 4, row, curses.color_pair(5))
    stdscr.refresh()


def draw_status_bar(stdscr, message):
    """Рисуем строку состояния внизу экрана."""
    height, width = stdscr.getmaxyx()
    stdscr.attron(curses.color_pair(7))
    safe_addstr(stdscr, height - 1, 0, " " * (width - 1))
    safe_addstr(stdscr, height - 1, 0, message)
    stdscr.attroff(curses.color_pair(7))
    stdscr.refresh()


# ---------------------------------------------------------------------------
# Вспомогательные сетевые функции
# ---------------------------------------------------------------------------

def get_gateway_for_target(target_ip):
    """Возвращает gateway (роутер) для подсети, в которой находится target_ip."""
    try:
        gws = netifaces.gateways()
        default_gws = gws.get('default', {})
        if netifaces.AF_INET in default_gws:
            return default_gws[netifaces.AF_INET][0]
        for af, gw_list in gws.items():
            if af == netifaces.AF_INET:
                for gw in gw_list:
                    gw_ip, iface, *_ = gw
                    addrs = netifaces.ifaddresses(iface)
                    if netifaces.AF_INET in addrs:
                        for addr in addrs[netifaces.AF_INET]:
                            ip = addr.get('addr')
                            if ip:
                                net = ipaddress.ip_network(ip + '/24', strict=False)
                                if ipaddress.ip_address(target_ip) in net:
                                    return gw_ip
    except Exception:
        pass
    return None


def get_local_ip_for_target(target_ip):
    """Возвращает локальный IP, находящийся в одной сети с target_ip."""
    try:
        target_net = ipaddress.ip_network(target_ip + '/24', strict=False)
        for iface in netifaces.interfaces():
            addrs = netifaces.ifaddresses(iface)
            if netifaces.AF_INET in addrs:
                for addr in addrs[netifaces.AF_INET]:
                    ip = addr.get('addr')
                    if ip and ipaddress.ip_address(ip) in target_net:
                        return ip
    except Exception:
        pass
    return None


# ---------------------------------------------------------------------------
# UI выбора устройств
# ---------------------------------------------------------------------------

def select_devices_ui(stdscr, devices):
    """Интерактивный выбор одного или нескольких устройств из списка."""
    if not devices:
        safe_addstr(stdscr, 2, 2, "Нет доступных устройств для выбора.", curses.color_pair(3))
        stdscr.refresh()
        stdscr.getch()
        return []

    selection_cursor = 0
    selected_indexes = set()

    while True:
        stdscr.clear()
        for i, line in enumerate(logo_art):
            safe_addstr(stdscr, i, 0, line, curses.color_pair(1))

        safe_addstr(stdscr, 12, 2, "=== Выбор устройств для аудита ===", curses.A_BOLD | curses.color_pair(2))
        safe_addstr(stdscr, 13, 2, "Space: выбрать, Enter: подтвердить, Q: назад", curses.color_pair(3))

        max_rows = max(5, stdscr.getmaxyx()[0] - 18)
        window_start = max(0, selection_cursor - max_rows + 1)
        window_end = min(len(devices), window_start + max_rows)

        row_y = 15
        for idx in range(window_start, window_end):
            device = devices[idx]
            ip = device.get("ip", "?") if isinstance(device, dict) else str(device)
            mac = device.get("mac", "?") if isinstance(device, dict) else "?"
            mark = "[x]" if idx in selected_indexes else "[ ]"
            row_text = f"{mark} {ip}  {mac}"

            if idx == selection_cursor:
                stdscr.attron(curses.color_pair(4))
                safe_addstr(stdscr, row_y, 2, row_text)
                stdscr.attroff(curses.color_pair(4))
            else:
                safe_addstr(stdscr, row_y, 2, row_text, curses.color_pair(5))
            row_y += 1

        draw_status_bar(stdscr, f"Выбрано устройств: {len(selected_indexes)}")
        stdscr.refresh()

        key = stdscr.getch()
        if key == curses.KEY_UP and selection_cursor > 0:
            selection_cursor -= 1
        elif key == curses.KEY_DOWN and selection_cursor < len(devices) - 1:
            selection_cursor += 1
        elif key == ord(' '):
            if selection_cursor in selected_indexes:
                selected_indexes.remove(selection_cursor)
            else:
                selected_indexes.add(selection_cursor)
        elif key in [10, 13]:
            break
        elif key in [ord('q'), ord('Q')]:
            return []

    return [devices[idx] for idx in sorted(selected_indexes)]


# ---------------------------------------------------------------------------
# Экраны меню
# ---------------------------------------------------------------------------

def main_menu(stdscr):
    curses.curs_set(0)  # Скрываем курсор
    stdscr.clear()
    stdscr.refresh()

    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)    # Цвет логотипа
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Цвет заголовка меню
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)   # Цвет инструкции
    curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)   # Цвет подсвеченного элемента меню
    curses.init_pair(5, curses.COLOR_BLUE, curses.COLOR_BLACK)    # Цвет обычного элемента меню
    curses.init_pair(6, curses.COLOR_MAGENTA, curses.COLOR_BLACK) # Цвет рамки
    curses.init_pair(7, curses.COLOR_BLACK, curses.COLOR_WHITE)   # Цвет строки состояния

    current_row = 0
    menu = [
        "Сканировать сеть",
        "Запустить ARP Spoofing",
        "Восстановить таблицы ARP",
        "Запустить прокси-сервер",
        "Установить зависимости",
        "Выход",
    ]

    while True:
        draw_logo_and_menu(stdscr, current_row, menu)
        draw_status_bar(stdscr, "Статус: Готово | Используйте стрелки для навигации | Нажмите Enter для выбора.")

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
                proxy_server_ui(stdscr)
            elif current_row == 4:
                install_dependencies_ui(stdscr)
            elif current_row == 5:
                break


def scan_network_ui(stdscr):
    stdscr.clear()
    for i, line in enumerate(logo_art):
        safe_addstr(stdscr, i, 0, line, curses.color_pair(1))
    draw_bordered_window(stdscr, len(logo_art) + 1, 0, 10, 50)
    current_line = 14
    safe_addstr(stdscr, current_line, 2, "=== Сканирование сети ===", curses.A_BOLD | curses.color_pair(2))
    current_line += 2
    safe_addstr(stdscr, current_line, 4, "Сканирование сети, пожалуйста, подождите...", curses.color_pair(3))
    stdscr.refresh()

    devices = scan_network()
    current_line += 2

    if not devices:
        safe_addstr(stdscr, current_line, 4, "Устройства не найдены.", curses.color_pair(3))
        safe_addstr(stdscr, current_line + 2, 2, "Нажмите любую клавишу, чтобы вернуться в меню...", curses.color_pair(3))
        stdscr.refresh()
        draw_status_bar(stdscr, "Статус: Сканирование | Устройства не найдены")
        stdscr.getch()
        return

    selection_cursor = 0
    selected_indexes = set()

    while True:
        stdscr.clear()
        for i, line in enumerate(logo_art):
            safe_addstr(stdscr, i, 0, line, curses.color_pair(1))

        safe_addstr(stdscr, 12, 2, "=== Выбор устройств (аудит) ===", curses.A_BOLD | curses.color_pair(2))
        safe_addstr(stdscr, 13, 2, "Space: выбрать, Enter: подтвердить, Q: назад", curses.color_pair(3))

        max_rows = max(5, stdscr.getmaxyx()[0] - 18)
        window_start = max(0, selection_cursor - max_rows + 1)
        window_end = min(len(devices), window_start + max_rows)

        row_y = 15
        for idx in range(window_start, window_end):
            device = devices[idx]
            ip = device.get("ip", "?") if isinstance(device, dict) else str(device)
            mac = device.get("mac", "?") if isinstance(device, dict) else "?"
            mark = "[x]" if idx in selected_indexes else "[ ]"
            row_text = f"{mark} {ip}  {mac}"

            if idx == selection_cursor:
                stdscr.attron(curses.color_pair(4))
                safe_addstr(stdscr, row_y, 2, row_text)
                stdscr.attroff(curses.color_pair(4))
            else:
                safe_addstr(stdscr, row_y, 2, row_text, curses.color_pair(5))
            row_y += 1

        draw_status_bar(stdscr, f"Выбрано устройств: {len(selected_indexes)}")
        stdscr.refresh()

        key = stdscr.getch()
        if key == curses.KEY_UP and selection_cursor > 0:
            selection_cursor -= 1
        elif key == curses.KEY_DOWN and selection_cursor < len(devices) - 1:
            selection_cursor += 1
        elif key == ord(' '):
            if selection_cursor in selected_indexes:
                selected_indexes.remove(selection_cursor)
            else:
                selected_indexes.add(selection_cursor)
        elif key in [10, 13]:
            break
        elif key in [ord('q'), ord('Q')]:
            return

    stdscr.clear()
    safe_addstr(stdscr, 2, 2, "=== Итог выбора устройств ===", curses.A_BOLD | curses.color_pair(2))
    if not selected_indexes:
        safe_addstr(stdscr, 4, 2, "Ничего не выбрано.", curses.color_pair(3))
    else:
        y = 4
        for idx in sorted(selected_indexes):
            device = devices[idx]
            ip = device.get("ip", "?") if isinstance(device, dict) else str(device)
            mac = device.get("mac", "?") if isinstance(device, dict) else "?"
            safe_addstr(stdscr, y, 2, f"- {ip} ({mac})", curses.color_pair(3))
            y += 1

    safe_addstr(stdscr, stdscr.getmaxyx()[0] - 2, 2, "Нажмите любую клавишу, чтобы вернуться в меню...", curses.color_pair(3))
    stdscr.refresh()
    stdscr.getch()


def arp_spoofing_ui(stdscr):
    stdscr.clear()
    for i, line in enumerate(logo_art):
        safe_addstr(stdscr, i, 0, line, curses.color_pair(1))
    draw_bordered_window(stdscr, len(logo_art) + 1, 0, 10, 50)
    safe_addstr(stdscr, 12, 2, "=== Выбор целей для аудита ===", curses.A_BOLD | curses.color_pair(2))
    safe_addstr(stdscr, 13, 2, "Space: выбрать, Enter: подтвердить, Q: назад", curses.color_pair(3))
    stdscr.refresh()

    devices = scan_network()
    selected_devices = select_devices_ui(stdscr, devices)

    target_ips = [d.get("ip") if isinstance(d, dict) else str(d) for d in selected_devices if d]

    stdscr.clear()
    safe_addstr(stdscr, 2, 2, "=== Итог выбора целей ===", curses.A_BOLD | curses.color_pair(2))
    if not target_ips:
        safe_addstr(stdscr, 4, 2, "Ничего не выбрано.", curses.color_pair(3))
    else:
        nets = defaultdict(list)
        for ip in target_ips:
            try:
                net = str(ipaddress.ip_network(ip + '/24', strict=False))
            except Exception:
                net = 'unknown'
            nets[net].append(ip)

        y = 4
        for net, ips in nets.items():
            safe_addstr(stdscr, y, 2, f"Подсеть: {net}", curses.A_BOLD | curses.color_pair(2))
            local_ip = get_local_ip_for_target(ips[0])
            gateway_ip = get_gateway_for_target(ips[0])
            if local_ip:
                safe_addstr(stdscr, y + 1, 4, f"IP вашей сети: {local_ip}", curses.color_pair(2))
            else:
                safe_addstr(stdscr, y + 1, 4, "IP вашей сети: не найден", curses.color_pair(3))
            if gateway_ip:
                safe_addstr(stdscr, y + 2, 4, f"Gateway: {gateway_ip}", curses.color_pair(2))
            else:
                safe_addstr(stdscr, y + 2, 4, "Gateway: не найден", curses.color_pair(3))
            y += 3
            safe_addstr(stdscr, y, 4, "Цели:", curses.A_BOLD | curses.color_pair(2))
            y += 1
            for ip in ips:
                safe_addstr(stdscr, y, 6, f"- {ip}", curses.color_pair(3))
                y += 1

    safe_addstr(stdscr, stdscr.getmaxyx()[0] - 4, 2, "Нажмите Enter для передачи в spoof-логику, Q — отмена", curses.color_pair(3))
    stdscr.refresh()

    while True:
        key = stdscr.getch()
        if key in [10, 13]:
            break
        elif key in [ord('q'), ord('Q')]:
            return

    nets = defaultdict(list)
    for ip in target_ips:
        try:
            net = str(ipaddress.ip_network(ip + '/24', strict=False))
        except Exception:
            net = 'unknown'
        nets[net].append(ip)

    for net, ips in nets.items():
        gateway_ip = get_gateway_for_target(ips[0])
        if gateway_ip:
            try:
                arp_spoof_attack(ips, gateway_ip)
            except Exception as e:
                safe_addstr(stdscr, stdscr.getmaxyx()[0] - 2, 2, f"Ошибка: {e}", curses.color_pair(3))
                stdscr.refresh()
                stdscr.getch()


def restore_arp_ui(stdscr):
    stdscr.clear()
    for i, line in enumerate(logo_art):
        safe_addstr(stdscr, i, 0, line, curses.color_pair(1))
    draw_bordered_window(stdscr, len(logo_art) + 1, 0, 10, 50)
    safe_addstr(stdscr, 12, 2, "=== Восстановление таблиц ARP ===", curses.A_BOLD | curses.color_pair(2))
    safe_addstr(stdscr, 13, 2, "Сканируем сеть для выбора цели...", curses.color_pair(3))
    stdscr.refresh()

    devices = scan_network()
    selected_devices = select_devices_ui(stdscr, devices)

    target_ips = [d.get("ip") if isinstance(d, dict) else str(d) for d in selected_devices if d]

    if not target_ips:
        stdscr.clear()
        safe_addstr(stdscr, 2, 2, "Устройства не выбраны. Восстановление отменено.", curses.color_pair(3))
        safe_addstr(stdscr, 4, 2, "Нажмите любую клавишу, чтобы вернуться в меню...", curses.color_pair(3))
        stdscr.refresh()
        stdscr.getch()
        return

    stdscr.clear()
    safe_addstr(stdscr, 2, 2, "=== Восстановление таблиц ARP ===", curses.A_BOLD | curses.color_pair(2))
    safe_addstr(stdscr, 4, 4, "Восстанавливаем таблицы ARP...", curses.color_pair(3))
    stdscr.refresh()

    y = 6
    for target_ip in target_ips:
        gateway_ip = get_gateway_for_target(target_ip)
        if gateway_ip:
            try:
                restore_arp(target_ip, gateway_ip)
                safe_addstr(stdscr, y, 4, f"[OK] {target_ip} восстановлен", curses.color_pair(4))
            except Exception as e:
                safe_addstr(stdscr, y, 4, f"[ERR] {target_ip}: {e}", curses.color_pair(3))
        else:
            safe_addstr(stdscr, y, 4, f"[SKIP] {target_ip}: gateway не найден", curses.color_pair(3))
        y += 1

    safe_addstr(stdscr, y + 1, 2, "Нажмите любую клавишу, чтобы вернуться в меню...", curses.color_pair(3))
    stdscr.refresh()
    stdscr.getch()


def proxy_server_ui(stdscr):
    stdscr.clear()
    for i, line in enumerate(logo_art):
        safe_addstr(stdscr, i, 0, line, curses.color_pair(1))
    draw_bordered_window(stdscr, len(logo_art) + 1, 0, 10, 50)
    header_y = len(logo_art) + 2
    hint_y = header_y + 2
    status_y = hint_y + 2
    safe_addstr(stdscr, header_y, 2, "=== Прокси-сервер (mitmproxy) ===", curses.A_BOLD | curses.color_pair(2))

    if proxy_server.is_running():
        safe_addstr(stdscr, hint_y, 4, "Прокси уже запущен. Нажмите S для остановки, Q — назад.", curses.color_pair(3))
    else:
        safe_addstr(stdscr, hint_y, 4, "Нажмите Enter для запуска прокси (порт 8080), Q — назад.", curses.color_pair(3))

    draw_status_bar(stdscr, "Статус: Прокси-сервер")
    stdscr.refresh()

    while True:
        key = stdscr.getch()
        if key in [10, 13] and not proxy_server.is_running():
            error_msg = None
            try:
                enable_ip_forwarding()
            except Exception as e:
                error_msg = f"Ошибка включения IP-форвардинга: {e}"
            if error_msg is None:
                try:
                    setup_iptables()
                except Exception as e:
                    error_msg = f"Ошибка настройки iptables: {e}"
            if error_msg is None:
                try:
                    proxy_server.start_proxy(port=8080)
                    safe_addstr(stdscr, status_y, 4, "Прокси запущен на порту 8080. Нажмите S для остановки.", curses.color_pair(4))
                except Exception as e:
                    error_msg = f"Ошибка запуска прокси: {e}"
            if error_msg:
                safe_addstr(stdscr, status_y, 4, error_msg, curses.color_pair(3))
            stdscr.refresh()
        elif key in [ord('s'), ord('S')] and proxy_server.is_running():
            try:
                proxy_server.stop_proxy()
            finally:
                clear_iptables()
                disable_ip_forwarding()
            safe_addstr(stdscr, status_y, 4, "Прокси остановлен.                                    ", curses.color_pair(3))
            stdscr.refresh()
        elif key in [ord('q'), ord('Q')]:
            return


def install_dependencies_ui(stdscr):
    stdscr.clear()
    for i, line in enumerate(logo_art):
        safe_addstr(stdscr, i, 0, line, curses.color_pair(1))
    draw_bordered_window(stdscr, len(logo_art) + 1, 0, 10, 50)
    safe_addstr(stdscr, len(logo_art) + 2, 2, "=== Установка зависимостей ===", curses.A_BOLD | curses.color_pair(2))
    safe_addstr(stdscr, len(logo_art) + 4, 4, "Устанавливаем зависимости...", curses.color_pair(3))
    stdscr.refresh()
    install_dependencies()
    safe_addstr(stdscr, len(logo_art) + 6, 2, "Зависимости установлены. Нажмите любую клавишу, чтобы вернуться в меню...", curses.color_pair(3))
    stdscr.refresh()
    stdscr.getch()


if __name__ == '__main__':
    curses.wrapper(main_menu)
