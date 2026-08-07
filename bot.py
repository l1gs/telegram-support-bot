import telebot
from telebot.types import Message
from config import TOKEN, ADMIN_ID
import json
import os

bot = telebot.TeleBot(TOKEN)

DB = "users.json"

if not os.path.exists(DB):
    with open(DB, "w") as f:
        json.dump({}, f)

def load():
    with open(DB, "r") as f:
        return json.load(f)

def save(data):
    with open(DB, "w") as f:
        json.dump(data, f)

@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(message, "أرسل رسالتك إلى الإدارة.")

@bot.message_handler(func=lambda m: True, content_types=[
    "text","photo","video","document","voice","audio","sticker"
])
def handler(message):

    db = load()

    if message.from_user.id == ADMIN_ID:

        if not message.reply_to_message:
            return

        key = str(message.reply_to_message.message_id)

        if key not in db:
            return

        bot.copy_message(
            chat_id=db[key],
            from_chat_id=message.chat.id,
            message_id=message.message_id
        )

        return

    sent = bot.copy_message(
        chat_id=ADMIN_ID,
        from_chat_id=message.chat.id,
        message_id=message.message_id
    )

    db[str(sent.message_id)] = message.chat.id
    save(db)
@bot.message_handler(commands=["users"])
def users_count(message):
    if message.from_user.id != ADMIN_ID:
        return

    db = load()

    ids = []

    for i in db.values():
        if i not in ids:
            ids.append(i)

    bot.send_message(
        ADMIN_ID,
        f"👥 عدد المستخدمين: {len(ids)}"
    )
print("Bot Started")
bot.infinity_polling(skip_pending=True)
