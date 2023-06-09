from math import ceil

import requests
import telebot
from datetime import datetime
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

bot_token_2 = "6077204161:AAGKxrXF7mMt7mYkljwVX_9R0c0-RkzSDRw"
task_bot = telebot.TeleBot(bot_token_2)

URL = "http://localhost:8000/task/tasks/"

keyboard = ReplyKeyboardMarkup(row_width=1)
button = KeyboardButton("/help")
keyboard.add(button)

ITEMS_PER_PAGE = 2
tasks_list = []
total_pages = 0

def check_id(message, number):
    try:
        int(number)
    except ValueError:
        task_bot.send_message(message.chat.id, "ID повинне бути числом")
        return False
    return True


def check_title(message, title):
    if title is None:
        task_bot.send_message(message.chat.id, "Заголовок не введено")
        return False
    return True


def check_connect(url):
    try:
        requests.get(url)
    except requests.exceptions.ConnectionError:
        return False
    return True


def check_date(message, date):
    try:
        due_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        return False
    return due_date


@task_bot.message_handler(commands=["start", "help"])
def start(message):
    task_bot.send_message(
        message.chat.id,
        "Вітаю! Я бот для завдань. Використовуйте команди:\n"
        "/help - для виведення довідки\n"
        "/create - для створення завдань\n"
        "/update - для оновлення завдань\n"
        "/complete - для оновлення статусу задачі\n"
        "/list - для виведення списку завдань\n"
        "/view - для вибору завдання\n"
        "/delete - для видалення завдань",
        reply_markup=keyboard
    )

@task_bot.message_handler(commands=["list"])
def task_list(message):

    if not check_connect(URL):
        task_bot.send_message(message.chat.id, "Сервер не відповідає")
        return

    response = requests.get(URL)
    tasks = response.json()

    if tasks:
        global total_pages, tasks_list
        tasks_list = tasks
        total_pages = ceil(len(tasks) / ITEMS_PER_PAGE)

        page = 1
        send_task_page(message, tasks_list, page, total_pages)
    else:
        task_bot.send_message(message.chat.id, "У вас немає заміток")


@task_bot.callback_query_handler(func=lambda call: call.data.startswith("list_page#"))
def handle_list_page_callback(call):
    page = int(call.data.split("#")[1])
    send_task_page(call.message, tasks_list, page, total_pages)
    task_bot.delete_message(call.message.chat.id, call.message.message_id)


def send_task_page(message, tasks, page, total_pages):
    start_index = (page - 1) * ITEMS_PER_PAGE
    end_index = start_index + ITEMS_PER_PAGE
    tasks_page = tasks[start_index:end_index]

    tasks_text = "\n".join([
        f"ID: {task['id']}, "
        f"Title: {task['title']}, "
        f"Description: {task['description']}, "
        f"Execution date: {task['due_date']}, "
        f"Completed: {task['completed']}, "
        for task in tasks_page
    ])

    pagination_text = f"Page {page}/{total_pages}"

    keyboard = InlineKeyboardMarkup()
    if page > 1:
        keyboard.add(InlineKeyboardButton("<< Перша", callback_data=f"list_page#1"))
        keyboard.add(InlineKeyboardButton("Previous", callback_data=f"list_page#{page - 1}"))
    if page < total_pages:
        keyboard.add(InlineKeyboardButton("Next", callback_data=f"list_page#{page + 1}"))
        keyboard.add(InlineKeyboardButton("Остання >>", callback_data=f"list_page#{total_pages}"))

    task_bot.send_message(message.chat.id, f"Список заміток:\n{tasks_text}\n\n{pagination_text}", reply_markup=keyboard)


@task_bot.message_handler(commands=["view"])
def view_task(message):
    task_bot.send_message(message.chat.id, "Введіть ID замітки:")
    task_bot.register_next_step_handler(message, get_task_by_id)


def get_task_by_id(message):
    if not check_id(message, message.text):
        return view_task(message)

    task_id = message.text
    url = f"{URL}{task_id}/"

    if not check_connect(url):
        task_bot.send_message(message.chat.id, "Сервер не відповідає")
        return

    response = requests.get(url)
    task = response.json()

    if task and response.status_code == 200:
        task_text = f"ID: {task['id']}, " \
                    f"Title: {task['title']}, " \
                    f"Description: {task['description']}, " \
                    f"Execution date: {task['due_date']}, " \
                    f"Completed: {task['completed']}"
        task_bot.send_message(message.chat.id, task_text)
    else:
        task_bot.send_message(message.chat.id, "Завдання не знайдена")


@task_bot.message_handler(commands=["delete"])
def delete_task(message):
    task_bot.send_message(message.chat.id, "Введіть ID завдання для видалення:")
    task_bot.register_next_step_handler(message, delete_task_by_id)


def delete_task_by_id(message):
    if not check_id(message, message.text):
        return delete_task(message)

    task_id = message.text
    url = f"{URL}{task_id}/"

    if not check_connect(url):
        task_bot.send_message(message.chat.id, "Сервер не відповідає")
        return

    response = requests.delete(url)

    if response.status_code == 204:
        task_bot.send_message(message.chat.id, "Завдання видалено")
    else:
        task_bot.send_message(message.chat.id, "Завдання не знайдено")


@task_bot.message_handler(commands=["complete"])
def complete_task(message):
    task_bot.send_message(message.chat.id, "Введіть ID завдання для оновлення статусу:")
    task_bot.register_next_step_handler(message, complete_task_by_id)


def complete_task_by_id(message):
    if not check_id(message, message.text):
        return complete_task(message)

    task_id = message.text
    url = f"{URL}{task_id}/"

    if not check_connect(url):
        task_bot.send_message(message.chat.id, "Сервер не відповідає")
        return

    response = requests.get(url)
    task = response.json()

    if task and response.status_code == 200:
        task["completed"] = True
        response = requests.put(url, task)
        task_bot.send_message(message.chat.id, "Статус завдання оновлено")
    else:
        task_bot.send_message(message.chat.id, "Завдання не знайдено")


@task_bot.message_handler(commands=["create"])
def create_task(message):
    task_bot.send_message(message.chat.id, "Введіть заголовок:")
    task_bot.register_next_step_handler(message, get_title)


def get_title(message):
    if not check_title(message, message.text):
        return create_task(message)

    title = message.text
    task_bot.send_message(message.chat.id, "Введіть опис:")
    task_bot.register_next_step_handler(message, get_description, title)


def get_description(message, title):
    description = message.text
    task_bot.send_message(message.chat.id, "Введіть дату виконання: (формат: YYYY-MM-DD)")
    task_bot.register_next_step_handler(message, get_due_date, title, description)


def get_due_date(message, title, description):
    if not check_date(message, message.text):
        return create_task(message)
    else:
        due_date = check_date(message, message.text)
    task = {
        "title": title,
        "description": description,
        "due_date": due_date,
        "completed": False
    }

    if not check_connect(URL):
        task_bot.send_message(message.chat.id, "Сервер не відповідає")
        return

    response = requests.post(URL, task)

    if response.status_code == 201:
        task_bot.send_message(message.chat.id, "Завдання створено")
    else:
        task_bot.send_message(message.chat.id, "Помилка при створенні завдання")


@task_bot.message_handler(commands=["update"])
def update_task(message):
    task_bot.send_message(message.chat.id, "Введіть ID завдання для оновлення:")
    task_bot.register_next_step_handler(message, get_id_for_update)


def get_id_for_update(message):
    if not check_id(message, message.text):
        return update_task(message)

    task_id = message.text
    task_bot.send_message(message.chat.id, "Введіть заголовок:")
    task_bot.register_next_step_handler(message, update_title, task_id)


def update_title(message, task_id):
    if not check_title(message, message.text):
        return update_task(message)

    title = message.text

    url = f"{URL}{task_id}/"
    if not check_connect(URL):
        task_bot.send_message(message.chat.id, "Сервер не відповідає")
        return

    json = {"title": title}
    response = requests.patch(url, json=json)

    if response.status_code == 200:
        task_bot.send_message(message.chat.id, "Завдання оновлено")
    else:
        task_bot.send_message(message.chat.id, "Помилка при оновленні завдання")


task_bot.polling(none_stop=True)
