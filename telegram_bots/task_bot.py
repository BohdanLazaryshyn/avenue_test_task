from math import ceil
import requests
import telebot
from telebot.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from dev_task_avenue.settings import TASK_API_URL, TASK_BOT_TOKEN

from telegram_bots.utils import (
    check_id,
    check_content,
    check_date,
    check_connect,
    check_cancel
)

task_bot = telebot.TeleBot(TASK_BOT_TOKEN)   # create bot

URL = TASK_API_URL   # url for requests

'''
This bot was written using "register_next_step_handler" method for complex commands.
'''

keyboard = ReplyKeyboardMarkup(row_width=1)   # create keyboard
button = KeyboardButton("/help")   # create button
keyboard.add(button)   # add button to keyboard

ITEMS_PER_PAGE = 2  # number of items per page
tasks_list = []  # list of tasks
total_pages = 0  # total number of pages


@task_bot.message_handler(commands=["start"])
def start(message):
    task_bot.send_message(
        message.chat.id,
        "Вітаю! Я бот для для користування вашим спиком завдань. "
        "Щоб отримати список команд використовуйте команду:\n"
        "/help - для виведення довідки\n"
    )


@task_bot.message_handler(commands=["help"])
def help_list(message):
    task_bot.send_message(
        message.chat.id,
        "Команди та можливості, які надає цей бот:\n"
        "/help - для виведення довідки\n"
        "/create - для створення завдань\n"
        "/update - для оновлення завдань\n"
        "/complete - для оновлення статусу задачі\n"
        "/list - для виведення списку завдань\n"
        "/view - для вибору завдання\n"
        "/delete - для видалення завдань\n"
        "/cancel - для відміни дії",
        reply_markup=keyboard
    )


@task_bot.message_handler(commands=["list"])
def task_list(message):

    if not check_connect(URL):
        task_bot.send_message(message.chat.id, "Сервер не відповідає")
        return

    response = requests.get(URL)
    tasks = response.json()

    if tasks:   # block for checking tasks and creating pagination
        global total_pages, tasks_list
        tasks_list = tasks
        total_pages = ceil(len(tasks) / ITEMS_PER_PAGE)

        page = 1
        send_task_page(message, tasks_list, page, total_pages)
    else:
        task_bot.send_message(message.chat.id, "У вас немає заміток")


@task_bot.callback_query_handler(func=lambda call: call.data.startswith("list_page#"))
def handle_list_page_callback(call):   # reaction to pagination buttons
    page = int(call.data.split("#")[1])
    send_task_page(call.message, tasks_list, page, total_pages)
    task_bot.delete_message(call.message.chat.id, call.message.message_id)


def send_task_page(message, tasks, page, pages):  # function for sending task page
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

    pagination_text = f"Page {page}/{pages}"

    keyboard = InlineKeyboardMarkup()  # create keyboard for pagination
    if page > 1:
        keyboard.add(InlineKeyboardButton("<< Перша", callback_data=f"list_page#1"))
        keyboard.add(InlineKeyboardButton("Previous", callback_data=f"list_page#{page - 1}"))
    if page < pages:
        keyboard.add(InlineKeyboardButton("Next", callback_data=f"list_page#{page + 1}"))
        keyboard.add(InlineKeyboardButton("Остання >>", callback_data=f"list_page#{pages}"))

    task_bot.send_message(
        message.chat.id,
        f"Список заміток:\n{tasks_text}\n"
        f"\n{pagination_text}",
        reply_markup=keyboard
    )


@task_bot.message_handler(commands=["view"])
def view_task(message):
    task_bot.send_message(message.chat.id, "Введіть ID замітки:")
    task_bot.register_next_step_handler(message, get_task_by_id)


def get_task_by_id(message):
    if check_cancel(message, task_bot):   # checking for cancel command
        return
    if not check_id(message, task_bot, message.text):  # checking for correct id
        return view_task(message)

    task_id = message.text
    url = f"{URL}{task_id}/"

    if not check_connect(url):  # checking for server connection
        task_bot.send_message(message.chat.id, "Сервер не відповідає")
        return

    response = requests.get(url)
    if response.status_code == 200:   # checking for existing task
        task = response.json()
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
    if check_cancel(message, task_bot):   # checking for cancel command
        return
    if not check_id(message, task_bot, message.text):  # checking for correct id
        return delete_task(message)

    task_id = message.text
    url = f"{URL}{task_id}/"

    if not check_connect(url):   # checking for server connection
        task_bot.send_message(message.chat.id, "Сервер не відповідає")
        return

    response = requests.delete(url)

    if response.status_code == 204:
        task_bot.send_message(message.chat.id, f"Завдання {task_id} видалено")
    else:
        task_bot.send_message(message.chat.id, "Завдання не знайдено")


@task_bot.message_handler(commands=["complete"])
def complete_task(message):
    task_bot.send_message(message.chat.id, "Введіть ID завдання для оновлення статусу:")
    task_bot.register_next_step_handler(message, complete_task_by_id)


def complete_task_by_id(message):
    if check_cancel(message, task_bot):   # checking for cancel command
        return
    if not check_id(message, task_bot, message.text):   # checking for correct id
        return complete_task(message)

    task_id = message.text
    url = f"{URL}{task_id}/"

    if not check_connect(url):   # checking for server connection
        task_bot.send_message(message.chat.id, "Сервер не відповідає")
        return

    response = requests.get(url)  # checking for existing task
    if response.status_code == 200:
        task = response.json()
        task["completed"] = True
        response = requests.put(url, task)
        task_bot.send_message(message.chat.id, f"Статус завдання {task_id} оновлено")
    else:
        task_bot.send_message(message.chat.id, "Завдання не знайдено")


@task_bot.message_handler(commands=["create"])
def create_task(message):
    task_bot.send_message(message.chat.id, "Введіть заголовок:")
    task_bot.register_next_step_handler(message, get_title)


def get_title(message):   # get title of task
    if check_cancel(message, task_bot):  # checking for cancel command
        return
    if not check_content(message, task_bot, message.text):  # checking for correct content
        return create_task(message)

    title = message.text
    task_bot.send_message(message.chat.id, "Введіть опис:")
    task_bot.register_next_step_handler(message, get_description, title)


def get_description(message, title):   # get description of task
    if check_cancel(message, task_bot):   # checking for cancel command
        return
    if not check_content(message, task_bot, message.text):  # checking for correct content
        return create_task(message)
    description = message.text
    task_bot.send_message(message.chat.id, "Введіть дату виконання: (формат: YYYY-MM-DD)")
    task_bot.register_next_step_handler(message, get_due_date, title, description)


def get_due_date(message, title, description):   # get due date of task
    if check_cancel(message, task_bot):   # checking for cancel command
        return
    if not check_date(message, task_bot, message.text):   # checking for correct date
        return create_task(message)
    else:
        due_date = check_date(message, task_bot, message.text)
    task = {
        "title": title,
        "description": description,
        "due_date": due_date,
        "completed": False
    }

    if not check_connect(URL):  # checking for server connection
        task_bot.send_message(message.chat.id, "Сервер не відповідає")
        return

    response = requests.post(URL, task)   # creating task

    if response.status_code == 201:  # checking for correct response
        task_bot.send_message(message.chat.id, "Завдання створено")
    else:
        task_bot.send_message(message.chat.id, "Помилка при створенні завдання")


@task_bot.message_handler(commands=["update"])
def update_task(message):
    task_bot.send_message(message.chat.id, "Введіть ID завдання для оновлення:")
    task_bot.register_next_step_handler(message, get_id_for_update)


def get_id_for_update(message):   # отримання ID для оновлення
    if check_cancel(message, task_bot):   # перевірка на відміну дії
        return
    if not check_id(message, task_bot, message.text):  # перевірка на коректність ID
        return update_task(message)

    task_id = message.text
    task_bot.send_message(message.chat.id, "Введіть заголовок:")
    task_bot.register_next_step_handler(message, update_title, task_id)


def update_title(message, task_id):   # отримання заголовку
    if check_cancel(message, task_bot):   # перевірка на відміну дії
        return
    if not check_content(message, task_bot, message.text):   # перевірка на наявність введення тексту
        return update_task(message)
    title = message.text

    url = f"{URL}{task_id}/"
    if not check_connect(URL):   # перевірка на доступність сервера
        task_bot.send_message(message.chat.id, "Сервер не відповідає")
        return
    response = requests.get(url)
    json = {"title": title}
    response = requests.patch(url, json=json)

    if response.status_code == 200:
        task_bot.send_message(message.chat.id, "Завдання оновлено")
    else:
        task_bot.send_message(message.chat.id, "Помилка при оновленні завдання")


task_bot.polling(none_stop=True)
