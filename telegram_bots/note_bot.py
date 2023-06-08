import requests
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

bot_token = "6000814952:AAGwaSXrmBlcPnNJjP9uoEo8ybmSKOkReCo"

bot = telebot.TeleBot(bot_token)
URL = "http://localhost:8000/note/notes/"


keyboard = ReplyKeyboardMarkup(row_width=1)
button = KeyboardButton("/help")
keyboard.add(button)


new_note = {}
update_note = {}
note_id = {}
delete_note = {}


def check_id(message, number):
    try:
        int(number)
    except ValueError:
        bot.send_message(message.chat.id, "ID повинне бути числом")
        return False
    return True


def check_title(message, title):
    if title is None:
        bot.send_message(message.chat.id, "Заголовок не введено")
        return False
    return True


def check_connect(url):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return False
    except requests.exceptions.ConnectionError:
        return False
    return True


def create_blank(message, blank, template):
    chat_id = message.chat.id
    blank[chat_id] = template


@bot.message_handler(commands=["start", "help"])
def start(message):
    bot.send_message(
        message.chat.id,
        "Вітаю! Я бот для заміток. Використовуйте команди:\n"
        "/help - для виведення довідки\n"
        "/create - для створення замітки\n"
        "/update - для оновлення замітки\n"
        "/list - для виведення списку заміток\n"
        "/view - для видалення замітки\n"
        "/delete - для видалення замітки",
        reply_markup=keyboard
    )


@bot.message_handler(commands=["create"])
def create_note(message):
    chat_id = message.chat.id
    new_note[chat_id] = {"title": None, "content": None}

    bot.send_message(chat_id, "Введіть заголовок замітки:")


@bot.message_handler(
    func=lambda message: message.chat.id in new_note and new_note[message.chat.id]["title"] is None
)
def save_title(message):
    chat_id = message.chat.id
    new_note[chat_id]["title"] = message.text
    if not check_title(message, new_note[chat_id]["title"]):
        return create_note(message)
    bot.send_message(chat_id, "Введіть вміст замітки:")


@bot.message_handler(
    func=lambda message: message.chat.id in new_note and new_note[message.chat.id]["content"] is None
)
def save_content(message):
    chat_id = message.chat.id
    new_note[chat_id]["content"] = message.text
    title = new_note[chat_id]["title"]
    content = new_note[chat_id]["content"]
    params = {
                    "title": title,
                    "content": content
                }
    if not check_connect(URL):
        bot.send_message(message.chat.id, "Помилка підключення")
        return
    response = requests.post(URL, json=params)
    bot.send_message(chat_id, f"Замітка створена\nTitle: {title}\nContent: {content} ")
    del new_note[chat_id]


@bot.message_handler(commands=["update"])
def update_note_title(message):
    chat_id = message.chat.id
    update_note[chat_id] = {"id": None, "content": None}

    bot.send_message(chat_id, "Введіть ID замітки:")


@bot.message_handler(
    func=lambda message: message.chat.id in update_note and update_note[message.chat.id]["id"] is None
)
def update_note_content(message):
    chat_id = message.chat.id
    update_note[chat_id]["id"] = message.text
    if not check_id(message, update_note[chat_id]["id"]):
        return update_note_title(message)
    bot.send_message(chat_id, "Введіть новий вміст замітки:")


@bot.message_handler(
    func=lambda message: message.chat.id in update_note and update_note[message.chat.id]["content"] is None
)
def update_note_content(message):
    chat_id = message.chat.id
    update_note[chat_id]["content"] = message.text
    id = update_note[chat_id]["id"]
    content = update_note[chat_id]["content"]
    params = {"content": content}
    url = URL + id + "/"
    if not check_connect(url):
        bot.send_message(message.chat.id, "Помилка підключення")
        return update_note_title(message)
    response = requests.patch(url, json=params)
    bot.send_message(chat_id, f"Замітка\n ID:{id} оновлена\n Новий вміст: {content}")
    del update_note[chat_id]


@bot.message_handler(commands=["list"])
def list_notes(message):

    if not check_connect(URL):
        bot.send_message(message.chat.id, "Помилка підключення")
        return

    response = requests.get(URL)
    notes = response.json()

    if notes:
        notes_text = "\n".join(
            [
                f"ID: {note['id']}, "
                f"Title: {note['title']}, "
                f"Content: {note['content']}" for note in notes
            ]
        )
        bot.send_message(message.chat.id, f"Список заміток:\n{notes_text}")
    else:
        bot.send_message(message.chat.id, "У вас немає заміток")


@bot.message_handler(commands=["view"])
def detail_note(message):
    chat_id = message.chat.id
    note_id[chat_id] = {"id": None}
    bot.send_message(chat_id, "Введіть ID замітки:")


@bot.message_handler(
    func=lambda message: message.chat.id in note_id and note_id[message.chat.id]["id"] is None
)
def get_id(message):
    chat_id = message.chat.id

    note_id[chat_id]["id"] = message.text
    if not check_id(message, note_id[chat_id]["id"]):
        return detail_note(message)

    url = f"{URL}{note_id[chat_id]['id']}/"
    if not check_connect(url):
        bot.send_message(message.chat.id, "Помилка підключення")
        return

    response = requests.get(url)
    note = response.json()

    bot.send_message(chat_id, f"Замітка \n ID: {note['id']}\n Title: {note['title']}\n Content: {note['content']}")

    del note_id[chat_id]


@bot.message_handler(commands=["delete"])
def delete_notes(message):
    chat_id = message.chat.id
    delete_note[chat_id] = {"id": None}

    bot.send_message(chat_id, "Введіть ID замітки:")


@bot.message_handler(
    func=lambda message: message.chat.id in delete_note and delete_note[message.chat.id]["id"] is None
)
def delete_id(message):
    chat_id = message.chat.id

    delete_note[chat_id]["id"] = message.text
    if not check_id(message, note_id[chat_id]["id"]):
        return delete_notes(message)

    url = f"{URL}{delete_note[chat_id]['id']}/"
    if not check_connect(url):
        bot.send_message(message.chat.id, "Помилка підключення")
        return

    response = requests.delete(url)
    bot.send_message(chat_id, f"Замітка з ID {delete_note[chat_id]['id']} видалена")
    del delete_note[chat_id]


bot.polling(none_stop=True)
