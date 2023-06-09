from datetime import datetime

import requests


def check_id(message, bot_name, number):
    try:
        int(number)
    except ValueError:
        bot_name.send_message(message.chat.id, "ID повинне бути числом")
        return False
    return True


def check_content(message, bot_name, content):
    if content is None:
        bot_name.send_message(message.chat.id, "Дані не введено")
        return False
    return True


def check_connect(url):
    try:
        requests.get(url)
    except requests.exceptions.ConnectionError:
        return False
    return True


def check_date(message, bot_name, date):
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
