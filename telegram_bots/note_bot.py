import requests
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

from dev_task_avenue.settings import NOTE_API_URL, NOTE_BOT_TOKEN
from telegram_bots.utils import check_id, check_content, check_connect

bot = telebot.TeleBot(NOTE_BOT_TOKEN)   # create bot
URL = NOTE_API_URL   # url for requests


keyboard = ReplyKeyboardMarkup(row_width=1)  # create keyboard
button = KeyboardButton("/help")   # create button
keyboard.add(button)  # add button to keyboard

'''
This bot was written using "lambda" in message handler for complex commands.
'''

new_note = {}  # create dict for new note
update_note = {}  # create dict for update note
note_id = {}  # create dict for detail note
delete_note = {}   # create dict for delete note


@bot.message_handler(commands=["start"])   # first message for user when he start bot
def start(message):
    bot.send_message(
        message.chat.id,
        "Вітаю! Я бот для заміток. "
        "Щоб отримати перелік моїх команд та можлвостей, використовуйте команду:\n"
        "/help - для виведення довідки\n"
    )


@bot.message_handler(commands=["help"])   # help for user when he need it
def help_list(message):   # list with commands
    bot.send_message(
        message.chat.id,
        "Команди та можливості, які надає цей бот:\n"
        "/help - для виведення довідки\n"
        "/create - для створення замітки\n"
        "/update - для оновлення замітки\n"
        "/list - для виведення списку заміток\n"
        "/view - для виведення замітки\n"
        "/delete - для видалення замітки",
        reply_markup=keyboard
    )


@bot.message_handler(commands=["create"])   # command for create new note in database
def create_note(message):
    chat_id = message.chat.id
    new_note[chat_id] = {"title": None, "content": None}

    bot.send_message(chat_id, "Введіть заголовок замітки:")


@bot.message_handler(
    func=lambda message: message.chat.id in new_note and new_note[message.chat.id]["title"] is None
)
def save_title(message):   # save title for new note
    chat_id = message.chat.id
    if not check_content(message, bot, message.text):
        return create_note(message)
    new_note[chat_id]["title"] = message.text
    bot.send_message(chat_id, "Введіть вміст замітки:")


@bot.message_handler(
    func=lambda message: message.chat.id in new_note and new_note[message.chat.id]["content"] is None
)
def save_content(message):                       # save content for new note
    chat_id = message.chat.id
    new_note[chat_id]["content"] = message.text
    title = new_note[chat_id]["title"]
    content = new_note[chat_id]["content"]
    params = {                                   # create params for request
                    "title": title,
                    "content": content
                }
    if not check_connect(URL):
        bot.send_message(message.chat.id, "Помилка підключення")
        return
    response = requests.post(URL, json=params)                     # send request to database for create new note
    bot.send_message(chat_id, f"Замітка створена\nTitle: {title}\nContent: {content} ")
    del new_note[chat_id]    # clear dict for new note


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

    if not check_id(message, bot, message.text):   # check id for update note
        return update_note_title(message)
    update_note[chat_id]["id"] = message.text

    bot.send_message(chat_id, "Введіть новий вміст замітки:")


@bot.message_handler(
    func=lambda message: message.chat.id in update_note and update_note[message.chat.id]["content"] is None
)
def update_note_content(message):                 # update content for note

    chat_id = message.chat.id
    id_note = update_note[chat_id]["id"]

    if not check_content(message, bot, message.text):    # check content for update note
        return update_note_title(message)
    content = message.text

    json = {"content": content}
    url = f"{URL}{id_note}/"
    if not check_connect(url):            # check connect to note
        bot.send_message(message.chat.id, "Помилка підключення")
        return update_note_title(message)

    response = requests.get(url)      # send request to database for update note
    if response.status_code == 200:
        response = requests.patch(url, json=json)
        bot.send_message(chat_id, f"Замітка\n ID:{id_note} оновлена\n Новий вміст: {content}")
    else:
        bot.send_message(chat_id, f"Замітка\n ID:{id_note} не знайдена")

    del update_note[chat_id]    # clear dict for update note


@bot.message_handler(commands=["list"])         # list with all notes
def list_notes(message):

    if not check_connect(URL):      # check connect to database
        bot.send_message(message.chat.id, "Помилка підключення")
        return

    response = requests.get(URL)
    notes = response.json()

    if notes:            # check notes in database
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


@bot.message_handler(commands=["view"])     # command for view note by id
def detail_note(message):
    chat_id = message.chat.id
    note_id[chat_id] = {"id": None}
    bot.send_message(chat_id, "Введіть ID замітки:")


@bot.message_handler(
    func=lambda message: message.chat.id in note_id and note_id[message.chat.id]["id"] is None
)
def get_note_by__id(message):
    chat_id = message.chat.id

    if not check_id(message, bot, message.text):        # check type of id for view note
        return detail_note(message)

    note_id[chat_id]["id"] = message.text
    url = f"{URL}{note_id[chat_id]['id']}/"

    if not check_connect(url):          # check connect to note by id in database
        bot.send_message(message.chat.id, "Помилка підключення")
        return

    response = requests.get(url)
    note = response.json()

    if note and response.status_code == 200:
        bot.send_message(                           # send message with note
            chat_id,
            f"Замітка \n "
            f"ID: {note['id']}\n "
            f"Title: {note['title']}\n "
            f"Content: {note['content']}"
        )
    else:
        bot.send_message(message.chat.id, "Завдання не знайдена")
    del note_id[chat_id]


@bot.message_handler(commands=["delete"])        # command for delete note by id
def delete_notes(message):
    chat_id = message.chat.id
    delete_note[chat_id] = {"id": None}

    bot.send_message(chat_id, "Введіть ID замітки:")


@bot.message_handler(
    func=lambda message: message.chat.id in delete_note and delete_note[message.chat.id]["id"] is None
)
def delete_id(message):

    chat_id = message.chat.id

    if not check_id(message, bot, message.text):            # check type of id for delete note
        return delete_notes(message)

    delete_note[chat_id]["id"] = message.text

    url = f"{URL}{delete_note[chat_id]['id']}/"
    if not check_connect(url):        # check connect to note in database
        bot.send_message(message.chat.id, "Помилка підключення")
        return

    response = requests.delete(url)             # send request to database for delete note
    if response.status_code == 204:
        bot.send_message(chat_id, f"Замітка з ID {delete_note[chat_id]['id']} видалена")
    else:
        bot.send_message(message.chat.id, "Завдання не знайдена")
    del delete_note[chat_id]


bot.polling(none_stop=True)
