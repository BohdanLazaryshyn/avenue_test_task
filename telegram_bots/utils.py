from datetime import datetime

import requests


def check_cancel(message, bot_name):   # перевірка на відміну команди
    if message.text == "/cancel":
        bot_name.send_message(message.chat.id, "Команда відмінена")
        return True
    return False


def check_id(message, bot_name, number):   # перевірка на відповідність ID
    try:
        int(number)
    except ValueError:
        bot_name.send_message(message.chat.id, "ID повинне бути числом, оберіть команду знову")
        return False
    return True


def check_content(message, bot_name, content):   # перевірка на наявність вмісту
    if content is None:
        bot_name.send_message(message.chat.id, "Дані не введено")
        return False
    return True


def check_connect(url):   # перевірка на підключення до сервера
    try:
        requests.get(url)
    except requests.exceptions.ConnectionError:
        return False
    return True


def check_date(message, bot_name, date):   # перевірка на відповідність дати
    try:
        due_date = datetime.strptime(date, "%Y-%m-%d").date()
        today = datetime.now().date()
        if due_date < today:
            bot_name.send_message(message.chat.id, "Введена дата менша за сьогоднішню")
            return False
    except ValueError:
        bot_name.send_message(message.chat.id, "Введена дата не дійсна")
        return False
    return due_date
