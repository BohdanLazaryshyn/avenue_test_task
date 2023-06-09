import requests
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

from telegram_bots.utils import check_id, check_content, check_connect

bot_token_1 = "6000814952:AAGwaSXrmBlcPnNJjP9uoEo8ybmSKOkReCo"

bot = telebot.TeleBot(bot_token_1)
URL = "http://localhost:8000/note/notes/"


keyboard = ReplyKeyboardMarkup(row_width=1)
button = KeyboardButton("/help")
keyboard.add(button)


new_note = {}
update_note = {}
note_id = {}
delete_note = {}


@bot.message_handler(commands=["start", "help"])
def start(message):
    bot.send_message(
        message.chat.id,
        "Вітаю! Я бот для заміток. Використовуйте команди:\n"
        "/help - для виведення довідки\n"
        "/create - для створення замітки\n"
        "/update - для оновлення замітки\n"
        "/list - для виведення списку заміток\n"
        "/view - для виведення замітки\n"
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
    if not check_content(message, bot, new_note[chat_id]["title"]):
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
    if not check_id(message, bot, update_note[chat_id]["id"]):
        return update_note_title(message)
    bot.send_message(chat_id, "Введіть новий вміст замітки:")


@bot.message_handler(
    func=lambda message: message.chat.id in update_note and update_note[message.chat.id]["content"] is None
)
def update_note_content(message):

    chat_id = message.chat.id
    id = update_note[chat_id]["id"]
    content = message.text

    json = {"content": content}
    url = f"{URL}{id}/"
    if not check_connect(url):
        bot.send_message(message.chat.id, "Помилка підключення")
        return update_note_title(message)

    response = requests.get(url)
    if response.status_code == 200:
        response = requests.patch(url, json=json)
        bot.send_message(chat_id, f"Замітка\n ID:{id} оновлена\n Новий вміст: {content}")
    else:
        bot.send_message(chat_id, f"Замітка\n ID:{id} не знайдена")

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
    if not check_id(message, bot, note_id[chat_id]["id"]):
        return detail_note(message)

    url = f"{URL}{note_id[chat_id]['id']}/"
    if not check_connect(url):
        bot.send_message(message.chat.id, "Помилка підключення")
        return

    response = requests.get(url)
    note = response.json()

    if note and response.status_code == 200:
        bot.send_message(chat_id, f"Замітка \n ID: {note['id']}\n Title: {note['title']}\n Content: {note['content']}")
    else:
        bot.send_message(message.chat.id, "Завдання не знайдена")
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
    if not check_id(message, bot, delete_note[chat_id]["id"]):
        return delete_notes(message)

    url = f"{URL}{delete_note[chat_id]['id']}/"
    if not check_connect(url):
        bot.send_message(message.chat.id, "Помилка підключення")
        return

    response = requests.delete(url)
    if response.status_code == 204:
        bot.send_message(chat_id, f"Замітка з ID {delete_note[chat_id]['id']} видалена")
    else:
        bot.send_message(message.chat.id, "Завдання не знайдена")
    del delete_note[chat_id]


bot.polling(none_stop=True)
