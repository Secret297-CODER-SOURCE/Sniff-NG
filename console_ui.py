import curses
import time
from arp_spoof import arp_spoof_attack, restore_arp
from network_scanner import scan_network
from dependency_manager import install_dependencies, enable_ip_forwarding, disable_ip_forwarding, setup_iptables, clear_iptables

<<<<<<< HEAD
# ASCII-логотип "Sniff-NG"
=======
# ASCII logo "Sniff-NG"
>>>>>>> 148822d0f62c4698e2825e9ce6910e3809af3b4c
logo_art = [
    "",
    "",
    "",
<<<<<<< HEAD
    # ASCII-логотип
=======
>>>>>>> 148822d0f62c4698e2825e9ce6910e3809af3b4c
    " ░▒▓███████▓▒░▒▓███████▓▒░░▒▓█▓▒░▒▓████████▓▒░▒▓████████▓▒░           ▒▓███████▓▒░ ░▒▓██████▓▒░  ",
    "░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░                 ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ ",
    "░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░                 ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░        ",
    " ░▒▓██████▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓██████▓▒░ ░▒▓██████▓▒░  ░▒▓███▓▒░ ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒▒▓███▓▒░ ",
    "       ░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░                 ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ ",
    "       ░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░                 ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ ",
    "░▒▓███████▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░                 ░▒▓█▓▒░░▒▓█▓▒░░▒▓██████▓▒░  ",
<<<<<<< HEAD
]

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
        stdscr.addstr(i, 0, line, curses.color_pair(1))  # Добавляем каждую строку с цветом "cyan"

    # Рисуем меню
    draw_bordered_window(stdscr, len(logo_art) + 1, 0, 10, 50)  # Рисуем окно с рамкой под логотипом
    stdscr.addstr(len(logo_art) + 2, 2, "=== Sniff-NG Меню ===", curses.A_BOLD | curses.color_pair(2))  # Добавляем заголовок меню
    stdscr.addstr(len(logo_art) + 4, 2, "Используйте стрелки для навигации и Enter для выбора.\n", curses.A_BOLD | curses.color_pair(3))  # Добавляем инструкции

    for idx, row in enumerate(menu):  # Проходим по элементам меню
        y_position = len(logo_art) + 6 + idx  # Рассчитываем вертикальную позицию для каждого элемента
        if idx == current_row:  # Подсвечиваем текущий элемент меню
            stdscr.attron(curses.color_pair(4))  # Устанавливаем цвет подсветки
            stdscr.addstr(y_position, 2, f"> {row}")  # Добавляем подсвеченный элемент меню
            stdscr.attroff(curses.color_pair(4))  # Отключаем подсветку
        else:
            stdscr.addstr(y_position, 4, row, curses.color_pair(5))  # Добавляем обычный элемент меню
    stdscr.refresh()  # Обновляем экран



def draw_status_bar(stdscr, message):
    """ Рисуем строку состояния внизу экрана. """
    height, width = stdscr.getmaxyx()  # Получаем размеры экрана
    stdscr.attron(curses.color_pair(7))  # Устанавливаем цвет для строки состояния
    stdscr.addstr(height - 1, 0, " " * (width - 1))  # Очищаем предыдущую строку состояния
    stdscr.addstr(height - 1, 0, message)  # Отображаем новое сообщение
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
    menu = ["Сканировать сеть", "Запустить ARP Spoofing", "Восстановить таблицы ARP", "Установить зависимости", "Выход"]  # Пункты меню

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
            elif current_row == 3:  # Если выбран пункт "Установить зависимости"
                install_dependencies_ui(stdscr)
            elif current_row == 4:  # Если выбран пункт "Выход"
                break  # Выходим из цикла и завершаем программу

def scan_network_ui(stdscr):
    stdscr.clear()  # Очищаем экран
    # Рисуем логотип
    for i, line in enumerate(logo_art):  # Проходим по каждой строке логотипа
        stdscr.addstr(i, 0, line, curses.color_pair(1))  # Добавляем каждую строку с цветом "cyan"
    current_line = 10  # Начинаем с 2 строки
    stdscr.addstr(current_line, 2, "=== Сканирование сети ===", curses.A_BOLD | curses.color_pair(2))  # Заголовок
    current_line += 2  # Переходим на следующую строку
    stdscr.addstr(current_line, 4, "Сканирование сети, пожалуйста, подождите...", curses.color_pair(3))  # Сообщение о процессе сканирования
    stdscr.refresh()  # Обновляем экран

    devices = scan_network()  # Выполняем функцию сканирования сети
    current_line += 2  # Переходим на 2 строки вниз

    if not devices:  # Если не найдено устройств
        stdscr.addstr(current_line, 4, "Устройства не найдены.", curses.color_pair(3))  # Сообщение об отсутствии устройств
    else:  # Если устройства найдены
        stdscr.addstr(current_line, 4, "Найденные устройства:", curses.color_pair(3))  # Сообщение о найденных устройствах
        current_line += 2  # Переходим на 2 строки вниз
        for device in devices:  # Проходим по каждому найденному устройству
            stdscr.addstr(current_line, 4, f"- {device}", curses.color_pair(5))  # Отображаем каждое устройство
            current_line += 1  # Переходим на следующую строку для следующего устройства
    stdscr.addstr(current_line + 2, 2, "Нажмите любую клавишу, чтобы вернуться в меню...", curses.color_pair(3))  # Сообщение для возврата в меню
    stdscr.refresh()  # Обновляем экран
    stdscr.getch()  # Ожидаем нажатия клавиши для возврата

def arp_spoofing_ui(stdscr):
    stdscr.clear()  # Очищаем экран
    # Рисуем логотип
    for i, line in enumerate(logo_art):  # Проходим по каждой строке логотипа
        stdscr.addstr(i, 0, line, curses.color_pair(1))  # Добавляем каждую строку с цветом "cyan"
    stdscr.addstr(2, 2, "=== Запуск ARP Spoofing ===", curses.A_BOLD | curses.color_pair(2))  # Заголовок
    stdscr.addstr(4, 4, "Выполняется ARP Spoofing атака...", curses.color_pair(3))  # Сообщение о выполнении ARP Spoofing
    stdscr.refresh()  # Обновляем экран
    arp_spoof_attack()  # Выполняем функцию ARP Spoofing
    stdscr.addstr(6, 2, "ARP Spoofing запущен. Нажмите любую клавишу, чтобы вернуться в меню...", curses.color_pair(3))  # Сообщение о завершении
    stdscr.refresh()  # Обновляем экран
    stdscr.getch()  # Ожидаем нажатия клавиши для возврата

def restore_arp_ui(stdscr):
    stdscr.clear()  # Очищаем экран
    # Рисуем логотип
    for i, line in enumerate(logo_art):  # Проходим по каждой строке логотипа
        stdscr.addstr(i, 0, line, curses.color_pair(1))  # Добавляем каждую строку с цветом "cyan"
    stdscr.addstr(2, 2, "=== Восстановление таблиц ARP ===", curses.A_BOLD | curses.color_pair(2))  # Заголовок
    stdscr.addstr(4, 4, "Восстанавливаем таблицы ARP...", curses.color_pair(3))  # Сообщение о процессе восстановления
    stdscr.refresh()  # Обновляем экран
    restore_arp()  # Выполняем функцию восстановления ARP
    stdscr.addstr(6, 2, "Таблицы ARP восстановлены. Нажмите любую клавишу, чтобы вернуться в меню...", curses.color_pair(3))  # Сообщение о завершении
    stdscr.refresh()  # Обновляем экран
    stdscr.getch()  # Ожидаем нажатия клавиши для возврата

def install_dependencies_ui(stdscr):
    stdscr.clear()  # Очищаем экран
    # Рисуем логотип
    for i, line in enumerate(logo_art):  # Проходим по каждой строке логотипа
        stdscr.addstr(i, 0, line, curses.color_pair(1))  # Добавляем каждую строку с цветом "cyan"
    stdscr.addstr(2, 2, "=== Установка зависимостей ===", curses.A_BOLD | curses.color_pair(2))  # Заголовок
    stdscr.addstr(4, 4, "Устанавливаем зависимости...", curses.color_pair(3))  # Сообщение о процессе установки
    stdscr.refresh()  # Обновляем экран
    install_dependencies()  # Выполняем функцию установки зависимостей
    stdscr.addstr(6, 2, "Зависимости установлены. Нажмите любую клавишу, чтобы вернуться в меню...", curses.color_pair(3))  # Сообщение о завершении
    stdscr.refresh()  # Обновляем экран
    stdscr.getch()  # Ожидаем нажатия клавиши для возврата

if __name__ == '__main__':
    curses.wrapper(main_menu)  # Инициализируем программу с оберткой curses
=======
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
>>>>>>> 148822d0f62c4698e2825e9ce6910e3809af3b4c
