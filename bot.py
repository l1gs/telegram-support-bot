import telebot
from telebot.types import Message
from config import TOKEN, ADMIN_ID

bot = telebot.TeleBot(TOKEN)

users = {}

@bot.message_handler(func=lambda m: True)
def all_messages(message: Message):
    # إذا كانت الرسالة من المدير
    if message.from_user.id == ADMIN_ID:
        if message.reply_to_message:
            txt = message.reply_to_message.text or ""
            if txt.startswith("ID:"):
                try:
                    user_id = int(txt.split("\n")[0].replace("ID:", ""))
                    bot.copy_message(
                        chat_id=user_id,
                        from_chat_id=message.chat.id,
                        message_id=message.message_id
                    )
                except:
                    pass
        return

    # إرسال رسالة المستخدم إلى المدير
    header = f"ID:{message.from_user.id}\n"
    if message.content_type == "text":
        bot.send_message(ADMIN_ID, header + message.text)
    else:
        bot.copy_message(
            chat_id=ADMIN_ID,
            from_chat_id=message.chat.id,
            message_id=message.message_id
        )

bot.infinity_polling()
