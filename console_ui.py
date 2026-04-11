def get_gateway_for_target(target_ip):
    """Возвращает gateway (роутер) для подсети, в которой находится target_ip."""
    try:
        gws = netifaces.gateways()
        default_gws = gws.get('default', {})
        # Обычно default_gws[netifaces.AF_INET] = (gateway_ip, iface)
        if netifaces.AF_INET in default_gws:
            return default_gws[netifaces.AF_INET][0]
        # Если несколько, ищем по интерфейсу
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
import netifaces
import ipaddress
import socket
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
while True:
    try:
        import curses
        import curses.textpad
        import time
        from arp_spoof import arp_spoof_attack, restore_arp, start_arp_spoof_thread, stop_arp_spoof_thread, is_arp_spoofing
        from network_scanner import scan_network, detect_default_gateway, scan_all_networks, scan_networks_recursive
        from dependency_manager import install_dependencies, enable_ip_forwarding, disable_ip_forwarding, setup_iptables, clear_iptables
        import proxy_server
        break
    except:
        from dependency_manager import install_dependencies, enable_ip_forwarding, disable_ip_forwarding, \
            setup_iptables, clear_iptables

        install_dependencies()
# Вспомогательная функция — извлекает IP из записи устройства
def _device_ip(device):
    """Возвращает IP-строку из dict или str; None если данных нет."""
    if not device:
        return None
    if isinstance(device, dict):
        return device.get("ip") or None
    val = str(device).strip()
    return val if val else None

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
    """ Рисуем окно с рамкой в заданной позиции с определенными размерами. """
    stdscr.attron(curses.color_pair(6))  # Устанавливаем цвет для рамки
    stdscr.border(0)  # Рисуем границу вокруг окна
    stdscr.attroff(curses.color_pair(6))  # Отключаем цвет

def draw_logo_and_menu(stdscr, current_row, menu):
    """ Рисуем логотип и меню на экране с улучшенным стилем. """
    stdscr.clear()  # Очищаем экран

    # Рисуем логотип
    for i, line in enumerate(logo_art):  # Проходим по каждой строке логотипа
        safe_addstr(stdscr, i, 0, line, curses.color_pair(1))  # Добавляем каждую строку с цветом "cyan"

    # Рисуем меню
    draw_bordered_window(stdscr, len(logo_art) + 1, 0, 10, 50)  # Рисуем окно с рамкой под логотипом
    safe_addstr(stdscr, len(logo_art) + 2, 2, "=== Sniff-NG Меню ===", curses.A_BOLD | curses.color_pair(2))  # Добавляем заголовок меню
    safe_addstr(stdscr, len(logo_art) + 4, 4, "WER1XY", curses.A_BOLD | curses.color_pair(1))  # ASCII-safe подпись
    safe_addstr(stdscr, len(logo_art) + 6, 2, "Используйте стрелки для навигации и Enter для выбора.", curses.A_BOLD | curses.color_pair(3))  # Добавляем инструкции

    for idx, row in enumerate(menu):  # Проходим по элементам меню
        y_position = len(logo_art) + 8 + idx  # Рассчитываем вертикальную позицию для каждого элемента
        if idx == current_row:  # Подсвечиваем текущий элемент меню
            stdscr.attron(curses.color_pair(4))  # Устанавливаем цвет подсветки
            safe_addstr(stdscr, y_position, 2, f"> {row}")  # Добавляем подсвеченный элемент меню
            stdscr.attroff(curses.color_pair(4))  # Отключаем подсветку
        else:
            safe_addstr(stdscr, y_position, 4, row, curses.color_pair(5))  # Добавляем обычный элемент меню
    stdscr.refresh()  # Обновляем экран



def draw_status_bar(stdscr, message):
    """ Рисуем строку состояния внизу экрана. """
    height, width = stdscr.getmaxyx()  # Получаем размеры экрана
    stdscr.attron(curses.color_pair(7))  # Устанавливаем цвет для строки состояния
    safe_addstr(stdscr, height - 1, 0, " " * (width - 1))  # Очищаем предыдущую строку состояния
    safe_addstr(stdscr, height - 1, 0, message)  # Отображаем новое сообщение
    stdscr.attroff(curses.color_pair(7))  # Отключаем цвет
    stdscr.refresh()  # Обновляем экран

def main_menu(stdscr):
    curses.curs_set(0)  # Скрываем курсор
    stdscr.clear()  # Очищаем экран
    stdscr.refresh()  # Обновляем экран

    # Инициализируем цветовые пары для разных элементов
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)    # Цвет логотипа
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Цвет заголовка меню
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)   # Цвет инструкции
    curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)   # Цвет подсвеченного элемента меню
    curses.init_pair(5, curses.COLOR_BLUE, curses.COLOR_BLACK)    # Цвет обычного элемента меню
    curses.init_pair(6, curses.COLOR_MAGENTA, curses.COLOR_BLACK) # Цвет рамки
    curses.init_pair(7, curses.COLOR_BLACK, curses.COLOR_WHITE)   # Цвет строки состояния

    current_row = 0  # Изначально выделена первая строка
    menu = ["Сканировать сеть", "Запустить ARP Spoofing", "Восстановить таблицы ARP", "MITM-прокси (перехват трафика)", "Установить зависимости", "Выход"]  # Пункты меню

    while True:
        draw_logo_and_menu(stdscr, current_row, menu)  # Рисуем логотип и меню
        draw_status_bar(stdscr, "Статус: Готово | Используйте стрелки для навигации | Нажмите Enter для выбора.")  # Показываем строку состояния

        key = stdscr.getch()  # Ждем ввода от пользователя

        if key == curses.KEY_UP and current_row > 0:  # Перемещение вверх в меню, если не на первой строке
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(menu) - 1:  # Перемещение вниз, если не на последней строке
            current_row += 1
        elif key in [curses.KEY_ENTER, 10, 13]:  # Нажата клавиша Enter
            if current_row == 0:  # Если выбран пункт "Сканировать сеть"
                scan_network_ui(stdscr)
            elif current_row == 1:  # Если выбран пункт "Запустить ARP Spoofing"
                arp_spoofing_ui(stdscr)
            elif current_row == 2:  # Если выбран пункт "Восстановить таблицы ARP"
                restore_arp_ui(stdscr)
            elif current_row == 3:  # Если выбран пункт "MITM-прокси"
                mitm_proxy_ui(stdscr)
            elif current_row == 4:  # Если выбран пункт "Установить зависимости"
                install_dependencies_ui(stdscr)
            elif current_row == 5:  # Если выбран пункт "Выход"
                break  # Выходим из цикла и завершаем программу

def scan_network_ui(stdscr):
    stdscr.clear()  # Очищаем экран
    # Рисуем логотип
    for i, line in enumerate(logo_art):  # Проходим по каждой строке логотипа
        safe_addstr(stdscr, i, 0, line, curses.color_pair(1))  # Добавляем каждую строку с цветом "cyan"
    draw_bordered_window(stdscr, len(logo_art) + 1, 0, 10, 50)  # Рисуем окно с рамкой под логотипом
    current_line = 14  # Начинаем с 2 строки
    safe_addstr(stdscr, current_line, 2, "=== Сканирование сети ===", curses.A_BOLD | curses.color_pair(2))  # Заголовок
    current_line += 2  # Переходим на следующую строку
    safe_addstr(stdscr, current_line, 4, "Сканирование сети, пожалуйста, подождите...", curses.color_pair(3))  # Сообщение о процессе сканирования
    stdscr.refresh()  # Обновляем экран

    devices = scan_network()  # Выполняем функцию сканирования сети
    current_line += 2  # Переходим на 2 строки вниз

    if not devices:  # Если не найдено устройств
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

    # Получаем список IP выбранных целей
    target_ips = [d.get("ip") if isinstance(d, dict) else str(d) for d in selected_devices if d]


    stdscr.clear()
    safe_addstr(stdscr, 2, 2, "=== Итог выбора целей ===", curses.A_BOLD | curses.color_pair(2))
    if not target_ips:
        safe_addstr(stdscr, 4, 2, "Ничего не выбрано.", curses.color_pair(3))
    else:
        # Группируем IP по подсетям
        from collections import defaultdict
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
                safe_addstr(stdscr, y + 1, 4, f"IP вашей сети: не найден", curses.color_pair(3))
            if gateway_ip:
                safe_addstr(stdscr, y + 2, 4, f"Gateway: {gateway_ip}", curses.color_pair(2))
            else:
                safe_addstr(stdscr, y + 2, 4, f"Gateway: не найден", curses.color_pair(3))
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

    # Для каждой подсети вызываем spoof-логику с ips и gateway
    from arp_spoof import arp_spoof_attack
    from collections import defaultdict
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
    stdscr.clear()  # Очищаем экран
    # Рисуем логотип
    for i, line in enumerate(logo_art):  # Проходим по каждой строке логотипа
        stdscr.addstr(i, 0, line, curses.color_pair(1))  # Добавляем каждую строку с цветом "cyan"
    draw_bordered_window(stdscr, len(logo_art) + 1, 0, 10, 50)  # Рисуем окно с рамкой под логотипом
    stdscr.addstr(2, 2, "=== Восстановление таблиц ARP ===", curses.A_BOLD | curses.color_pair(2))  # Заголовок
    stdscr.addstr(4, 4, "Восстанавливаем таблицы ARP...", curses.color_pair(3))  # Сообщение о процессе восстановления
    stdscr.refresh()  # Обновляем экран
    restore_arp(stdscr.getmaxyx,stdscr.getmaxyx)  # Выполняем функцию восстановления ARP
    stdscr.addstr(6, 2, "Таблицы ARP восстановлены. Нажмите любую клавишу, чтобы вернуться в меню...", curses.color_pair(3))  # Сообщение о завершении
    stdscr.refresh()  # Обновляем экран
    stdscr.getch()  # Ожидаем нажатия клавиши для возврата

def install_dependencies_ui(stdscr):
    stdscr.clear()  # Очищаем экран
    # Рисуем логотип
    for i, line in enumerate(logo_art):  # Проходим по каждой строке логотипа
        stdscr.addstr(i, 0, line, curses.color_pair(1))  # Добавляем каждую строку с цветом "cyan"
    draw_bordered_window(stdscr, len(logo_art) + 1, 0, 10, 50)  # Рисуем окно с рамкой под логотипом
    stdscr.addstr(2, 2, "=== Установка зависимостей ===", curses.A_BOLD | curses.color_pair(2))  # Заголовок
    stdscr.addstr(4, 4, "Устанавливаем зависимости...", curses.color_pair(3))  # Сообщение о процессе установки
    stdscr.refresh()  # Обновляем экран
    install_dependencies()  # Выполняем функцию установки зависимостей
    stdscr.addstr(6, 2, "Зависимости установлены. Нажмите любую клавишу, чтобы вернуться в меню...", curses.color_pair(3))  # Сообщение о завершении
    stdscr.refresh()  # Обновляем экран
    stdscr.getch()  # Ожидаем нажатия клавиши для возврата

def mitm_proxy_ui(stdscr):
    """
    Экран управления MITM-прокси.

    Позволяет:
      1. Выбрать целевые устройства.
      2. Включить IP-форвардинг + iptables-редирект (80/443 → 8080).
      3. Запустить ARP-спуфинг в фоне.
      4. Запустить mitmproxy (mitmdump) в прозрачном режиме.
      5. Остановить всё и восстановить сеть.
    """

    _targets = []       # список IP выбранных целей
    _gateway = None
    restore_errors = []  # ошибки при восстановлении ARP

    def _draw_status():
        stdscr.clear()
        for i, line in enumerate(logo_art):
            safe_addstr(stdscr, i, 0, line, curses.color_pair(1))

        safe_addstr(stdscr, 12, 2, "=== MITM-прокси (перехват трафика) ===", curses.A_BOLD | curses.color_pair(2))

        arp_status  = "✔ активен" if is_arp_spoofing()          else "✘ остановлен"
        prx_status  = "✔ активен" if proxy_server.is_running()  else "✘ остановлен"
        arp_color   = curses.color_pair(4) if is_arp_spoofing()         else curses.color_pair(3)
        prx_color   = curses.color_pair(4) if proxy_server.is_running() else curses.color_pair(3)

        safe_addstr(stdscr, 14, 2, f"ARP-спуфинг : {arp_status}", arp_color)
        safe_addstr(stdscr, 15, 2, f"mitmproxy   : {prx_status}", prx_color)

        if proxy_server.is_running():
            safe_addstr(stdscr, 16, 2,
                        f"Лог трафика : {proxy_server.get_log_file()}",
                        curses.color_pair(3))
            safe_addstr(stdscr, 17, 2,
                        f"Порт прокси : {proxy_server.get_port()}",
                        curses.color_pair(3))

        tgt_line = ", ".join(_targets) if _targets else "(не выбраны)"
        gw_line  = _gateway if _gateway else "(не определён)"
        safe_addstr(stdscr, 19, 2, f"Цели    : {tgt_line}",  curses.color_pair(3))
        safe_addstr(stdscr, 20, 2, f"Шлюз    : {gw_line}",   curses.color_pair(3))

        actions = []
        if not is_arp_spoofing() and not proxy_server.is_running():
            actions.append("[S] Выбрать цели и запустить MITM")
        else:
            actions.append("[X] Остановить MITM и восстановить сеть")
        actions.append("[Q] Вернуться в меню")

        y = 22
        for act in actions:
            safe_addstr(stdscr, y, 2, act, curses.color_pair(5))
            y += 1

        draw_status_bar(stdscr, "MITM-режим | S — старт | X — стоп | Q — выход")
        stdscr.refresh()

    def _start_mitm():
        nonlocal _targets, _gateway

        # 1. Сканируем и выбираем цели
        safe_addstr(stdscr, 24, 2, "Сканирование сети...", curses.color_pair(3))
        stdscr.refresh()
        devices = scan_network()
        selected = select_devices_ui(stdscr, devices)
        if not selected:
            return

        _targets = [_device_ip(d) for d in selected if _device_ip(d)]
        _gateway = get_gateway_for_target(_targets[0]) if _targets else None

        if not _gateway:
            _gateway = detect_default_gateway()

        if not _targets or not _gateway:
            _draw_status()
            safe_addstr(stdscr, 24, 2,
                        "Ошибка: не удалось определить цели или шлюз. Нажмите любую клавишу.",
                        curses.color_pair(3))
            stdscr.refresh()
            stdscr.getch()
            return

        # 2. Включаем IP-форвардинг
        enable_ip_forwarding()

        # 3. Настраиваем iptables-редирект
        setup_iptables()

        # 4. Запускаем ARP-спуфинг в фоне
        start_arp_spoof_thread(_targets, _gateway)

        # 5. Запускаем mitmproxy
        ok = proxy_server.start_mitmproxy()
        _draw_status()
        if not ok:
            safe_addstr(stdscr, 24, 2,
                        "Не удалось запустить mitmproxy. Проверьте, установлен ли пакет. Нажмите любую клавишу.",
                        curses.color_pair(3))
            stdscr.refresh()
            stdscr.getch()

    def _stop_mitm():
        nonlocal restore_errors
        # Останавливаем mitmproxy
        proxy_server.stop_mitmproxy()

        # Останавливаем ARP-спуфинг
        stop_arp_spoof_thread()

        # Восстанавливаем ARP-таблицы
        restore_errors = []
        if _targets and _gateway:
            for t in _targets:
                try:
                    restore_arp(t, _gateway)
                except Exception as e:
                    restore_errors.append(f"{t}: {e}")

        # Убираем iptables-правила
        clear_iptables()

        # Отключаем IP-форвардинг
        disable_ip_forwarding()

    while True:
        _draw_status()
        key = stdscr.getch()
        if key in [ord('q'), ord('Q')]:
            break
        elif key in [ord('s'), ord('S')]:
            if not is_arp_spoofing() and not proxy_server.is_running():
                _start_mitm()
        elif key in [ord('x'), ord('X')]:
            if is_arp_spoofing() or proxy_server.is_running():
                _stop_mitm()
                _draw_status()
                if restore_errors:
                    err_text = "; ".join(restore_errors[:3])
                    safe_addstr(stdscr, 24, 2,
                                f"Ошибки при восстановлении ARP: {err_text}. Нажмите любую клавишу.",
                                curses.color_pair(3))
                    stdscr.refresh()
                    stdscr.getch()
                restore_errors = []


def select_targets_from_all_networks_ui(stdscr):
    stdscr.clear()
    for i, line in enumerate(logo_art):
        safe_addstr(stdscr, i, 0, line, curses.color_pair(1))
    draw_bordered_window(stdscr, len(logo_art) + 1, 0, 10, 50)
    safe_addstr(stdscr, 12, 2, "=== Выбор целей из всех подсетей ===", curses.A_BOLD | curses.color_pair(2))
    safe_addstr(stdscr, 13, 2, "Space: выбрать, Enter: подтвердить, Q: назад", curses.color_pair(3))
    stdscr.refresh()

    all_devices = scan_all_networks()  # {subnet: [devices]}
    device_list = []
    subnet_map = {}
    for subnet, devices in all_devices.items():
        for dev in devices:
            device_list.append(dev)
            subnet_map[dev['ip']] = subnet

    selected_devices = select_devices_ui(stdscr, device_list)
    target_ips = [d.get("ip") for d in selected_devices if d]

    stdscr.clear()
    safe_addstr(stdscr, 2, 2, "=== Итог выбора целей ===", curses.A_BOLD | curses.color_pair(2))
    if not target_ips:
        safe_addstr(stdscr, 4, 2, "Ничего не выбрано.", curses.color_pair(3))
    else:
        from collections import defaultdict
        nets = defaultdict(list)
        for ip in target_ips:
            net = subnet_map.get(ip, 'unknown')
            nets[net].append(ip)
        y = 4
        for net, ips in nets.items():
            safe_addstr(stdscr, y, 2, f"Подсеть: {net}", curses.A_BOLD | curses.color_pair(2))
            local_ip = get_local_ip_for_target(ips[0])
            gateway_ip = get_gateway_for_target(ips[0])
            if local_ip:
                safe_addstr(stdscr, y + 1, 4, f"IP вашей сети: {local_ip}", curses.color_pair(2))
            else:
                safe_addstr(stdscr, y + 1, 4, f"IP вашей сети: не найден", curses.color_pair(3))
            if gateway_ip:
                safe_addstr(stdscr, y + 2, 4, f"Gateway: {gateway_ip}", curses.color_pair(2))
            else:
                safe_addstr(stdscr, y + 2, 4, f"Gateway: не найден", curses.color_pair(3))
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
    from arp_spoof import arp_spoof_attack
    for net, ips in nets.items():
        gateway_ip = get_gateway_for_target(ips[0])
        if gateway_ip:
            try:
                arp_spoof_attack(ips, gateway_ip)
            except Exception as e:
                safe_addstr(stdscr, stdscr.getmaxyx()[0] - 2, 2, f"Ошибка: {e}", curses.color_pair(3))
                stdscr.refresh()
                stdscr.getch()

def select_targets_from_all_networks_recursive_ui(stdscr):
    stdscr.clear()
    for i, line in enumerate(logo_art):
        safe_addstr(stdscr, i, 0, line, curses.color_pair(1))
    draw_bordered_window(stdscr, len(logo_art) + 1, 0, 10, 50)
    safe_addstr(stdscr, 12, 2, "=== Выбор целей из всех подсетей (рекурсивно) ===", curses.A_BOLD | curses.color_pair(2))
    safe_addstr(stdscr, 13, 2, "Space: выбрать, Enter: подтвердить, Q: назад", curses.color_pair(3))
    stdscr.refresh()

    all_devices = scan_networks_recursive(max_depth=2)  # {subnet: [devices]}
    device_list = []
    subnet_map = {}
    for subnet, devices in all_devices.items():
        for dev in devices:
            device_list.append(dev)
            subnet_map[dev['ip']] = subnet

    selected_devices = select_devices_ui(stdscr, device_list)
    target_ips = [d.get("ip") for d in selected_devices if d]

    stdscr.clear()
    safe_addstr(stdscr, 2, 2, "=== Итог выбора целей ===", curses.A_BOLD | curses.color_pair(2))
    if not target_ips:
        safe_addstr(stdscr, 4, 2, "Ничего не выбрано.", curses.color_pair(3))
    else:
        from collections import defaultdict
        nets = defaultdict(list)
        for ip in target_ips:
            net = subnet_map.get(ip, 'unknown')
            nets[net].append(ip)
        y = 4
        for net, ips in nets.items():
            safe_addstr(stdscr, y, 2, f"Подсеть: {net}", curses.A_BOLD | curses.color_pair(2))
            local_ip = get_local_ip_for_target(ips[0])
            gateway_ip = get_gateway_for_target(ips[0])
            if local_ip:
                safe_addstr(stdscr, y + 1, 4, f"IP вашей сети: {local_ip}", curses.color_pair(2))
            else:
                safe_addstr(stdscr, y + 1, 4, f"IP вашей сети: не найден", curses.color_pair(3))
            if gateway_ip:
                safe_addstr(stdscr, y + 2, 4, f"Gateway: {gateway_ip}", curses.color_pair(2))
            else:
                safe_addstr(stdscr, y + 2, 4, f"Gateway: не найден", curses.color_pair(3))
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
    from arp_spoof import arp_spoof_attack
    for net, ips in nets.items():
        gateway_ip = get_gateway_for_target(ips[0])
        if gateway_ip:
            try:
                arp_spoof_attack(ips, gateway_ip)
            except Exception as e:
                safe_addstr(stdscr, stdscr.getmaxyx()[0] - 2, 2, f"Ошибка: {e}", curses.color_pair(3))
                stdscr.refresh()
                stdscr.getch()

if __name__ == '__main__':
    curses.wrapper(main_menu)  # Инициализируем программу с оберткой curses
