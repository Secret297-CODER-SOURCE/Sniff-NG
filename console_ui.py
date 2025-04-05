while True:
    try:
        import curses
        import curses.textpad
        import time
        from arp_spoof import arp_spoof_attack, restore_arp
        from network_scanner import scan_network
        from dependency_manager import install_dependencies, enable_ip_forwarding, disable_ip_forwarding, setup_iptables, clear_iptables
        break
    except:
        from dependency_manager import install_dependencies, enable_ip_forwarding, disable_ip_forwarding, \
            setup_iptables, clear_iptables

        install_dependencies()
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
    stdscr.addstr(len(logo_art) + 4, 4, "❤️WER1XY❤️", curses.A_BOLD | curses.color_pair(1))  # Добавляем инструкции
    stdscr.addstr(len(logo_art) + 6, 2, "Используйте стрелки для навигации и Enter для выбора.\n", curses.A_BOLD | curses.color_pair(3))  # Добавляем инструкции

    for idx, row in enumerate(menu):  # Проходим по элементам меню
        y_position = len(logo_art) + 8 + idx  # Рассчитываем вертикальную позицию для каждого элемента
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
    draw_bordered_window(stdscr, len(logo_art) + 1, 0, 10, 50)  # Рисуем окно с рамкой под логотипом
    current_line = 14  # Начинаем с 2 строки
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
    draw_status_bar(stdscr,
                    "Статус: Сканирование | Нажмите Enter для выхода.")  # Показываем строку состояния
    stdscr.getch()  # Ожидаем нажатия клавиши для возврата

def arp_spoofing_ui(stdscr):
    stdscr.clear()  # Очищаем экран
    # Рисуем логотип
    for i, line in enumerate(logo_art):  # Проходим по каждой строке логотипа
        stdscr.addstr(i, 0, line, curses.color_pair(1))  # Добавляем каждую строку с цветом "cyan"
    draw_bordered_window(stdscr, len(logo_art) + 1, 0, 10, 50)  # Рисуем окно с рамкой под логотипом
    stdscr.addstr(12, 2, "=== Запуск ARP Spoofing ===", curses.A_BOLD | curses.color_pair(2))  # Заголовок

    # Ввод Target IP
    stdscr.addstr(16, 2, "Введите Target IP: ", curses.color_pair(2))  # Вопрос для ввода Target IP
    target_window = stdscr.subwin(1, 24, 16, 24)  # Создаем окно для ввода IP
    curses.textpad.rectangle(stdscr, 15, 22, 17, 48)  # Рисуем рамку для поля ввода
    target_box = curses.textpad.Textbox(target_window)  # Поле для ввода Target IP
    draw_status_bar(stdscr,
                    "Статус: ARP-Spoofing | Введите Target | Нажмите Enter для подтверждения.")
    # Ввод Gateway IP
    stdscr.addstr(20, 2, "Введите Gateway IP: ", curses.color_pair(2))  # Вопрос для ввода Gateway IP
    gateway_window = stdscr.subwin(1, 24, 20, 24)  # Создаем окно для ввода IP
    curses.textpad.rectangle(stdscr, 19, 22, 21, 48)  # Рисуем рамку для поля ввода
    gateway_box = curses.textpad.Textbox(gateway_window)  # Поле для ввода Gateway IP
    draw_status_bar(stdscr,
                    "Статус: ARP-Spoofing | Введите Gateway | Нажмите Enter для подтверждения.")
    stdscr.addstr(26, 2, "Нажмите CTRL+X для завершения ввода.", curses.color_pair(2))  # Сообщение о завершении ввода
    stdscr.refresh()  # Обновляем экран

    def custom_edit_textbox(textbox):
        """Функция для расширенного редактирования текста с заменой символа при удалении на пробел."""
        while True:
            char = textbox.win.getch()  # Чтение символа с клавиатуры
            if char == curses.KEY_BACKSPACE or char == 127:  # Обработка клавиши Backspace
                y, x = textbox.win.getyx()  # Получаем текущие координаты курсора
                if x > 0:  # Если не в начале строки
                    textbox.win.delch(y, x - 1)  # Удаляем символ слева от курсора
                    textbox.win.insch(y, x - 1, ' ')  # Вставляем пробел вместо удаленного символа
                    textbox.win.move(y, x - 1)  # Перемещаем курсор на позицию назад
            elif char == 10:  # Если нажата клавиша Enter, завершаем ввод
                break
            else:
                textbox.do_command(char)  # Все остальные символы передаем в стандартную обработку
        return textbox.gather()  # Возвращаем введенный текст

    # Получаем и обрабатываем введенные значения
    target_ip = custom_edit_textbox(target_box).strip()  # Получаем введенный Target IP
    gateway_ip = custom_edit_textbox(gateway_box).strip()  # Получаем введенный Gateway IP

    # Запускаем ARP Spoofing с введенными данными
    arp_spoof_attack(target_ip, gateway_ip)  # Выполняем функцию ARP Spoofing

    stdscr.addstr(22, 2, "ARP Spoofing запущен. Нажмите любую клавишу, чтобы вернуться в меню...",
                  curses.color_pair(3))  # Сообщение о завершении
    stdscr.refresh()  # Обновляем экран
    stdscr.getch()  # Ожидаем нажатия клавиши для возврата
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

if __name__ == '__main__':
    curses.wrapper(main_menu)  # Инициализируем программу с оберткой curses
