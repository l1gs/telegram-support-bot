import telebot
from telebot.types import Message
from config import TOKEN, ADMIN_ID

bot = telebot.TeleBot(TOKEN)

reply_map = {}

@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(message, "أرسل رسالتك إلى الإدارة.")

@bot.message_handler(func=lambda m: True, content_types=[
    "text","photo","video","document","voice","audio","sticker"
])
def handler(message):

    if message.from_user.id == ADMIN_ID:

        if not message.reply_to_message:
            return

        key = str(message.reply_to_message.message_id)

        if key not in reply_map:
            return

        user_id = reply_map[key]

        bot.copy_message(
            chat_id=user_id,
            from_chat_id=message.chat.id,
            message_id=message.message_id
        )

        return

    sent = bot.copy_message(
        chat_id=ADMIN_ID,
        from_chat_id=message.chat.id,
        message_id=message.message_id
    )

    reply_map[str(sent.message_id)] = message.chat.id

print("Bot Started")
bot.infinity_polling(skip_pending=True)
bot.infinity_polling()
