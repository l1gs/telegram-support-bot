import telebot
from telebot.types import Message
from config import TOKEN, ADMIN_ID
import json
import os

bot = telebot.TeleBot(TOKEN)

DB = "users.json"
BAN = "banned.json"

if not os.path.exists(DB):
    with open(DB, "w") as f:
        json.dump({}, f)

if not os.path.exists(BAN):
    with open(BAN, "w") as f:
        json.dump([], f)

def load_users():
    with open(DB, "r") as f:
        return json.load(f)

def save_users(data):
    with open(DB, "w") as f:
        json.dump(data, f)

def load_banned():
    with open(BAN, "r") as f:
        return json.load(f)

def save_banned(data):
    with open(BAN, "w") as f:
        json.dump(data, f)

@bot.message_handler(commands=["start"])
def start(message):
    if message.from_user.id in load_banned():
        return

    bot.reply_to(
        message,
        "👋 أهلاً بك\n\nأرسل رسالتك."
    )
    def is_banned(user_id):
    return user_id in load_banned()


def get_user_name(message):
    name = message.from_user.first_name or ""
    username = message.from_user.username

    if username:
        return f"{name} (@{username})"

    return name


@bot.message_handler(
    func=lambda message: message.from_user.id != ADMIN_ID,
    content_types=[
        "text",
        "photo",
        "video",
        "document",
        "audio",
        "voice",
        "sticker",
        "animation",
        "contact",
        "location"
    ]
)
def receive_user_message(message):

    user_id = message.from_user.id

    if is_banned(user_id):
        return

    db = load_users()

    # نرسل الرسالة إلى الإدارة
    if message.content_type == "text":

        sent = bot.send_message(
            ADMIN_ID,
            f"👤 {get_user_name(message)}\n"
            f"🆔 ID: {user_id}\n\n"
            f"{message.text}"
        )

    else:

        sent = bot.copy_message(
            ADMIN_ID,
            message.chat.id,
            message.message_id
        )

        bot.send_message(
            ADMIN_ID,
            f"👤 {get_user_name(message)}\n"
            f"🆔 ID: {user_id}",
            reply_to_message_id=sent.message_id
        )

    # ربط رسالة الإدارة بالمستخدم
    db[str(sent.message_id)] = user_id
    save_users(db)
    @bot.message_handler(
    func=lambda message: (
        message.from_user.id == ADMIN_ID
        and message.reply_to_message is not None
    ),
    content_types=[
        "text",
        "photo",
        "video",
        "document",
        "audio",
        "voice",
        "sticker",
        "animation",
        "contact",
        "location"
    ]
)
def admin_reply(message):

    db = load_users()

    replied_id = str(message.reply_to_message.message_id)

    if replied_id not in db:
        bot.send_message(
            ADMIN_ID,
            "⚠️ لم أجد المستخدم المرتبط بهذه الرسالة."
        )
        return

    user_id = int(db[replied_id])

    if is_banned(user_id):
        bot.send_message(
            ADMIN_ID,
            "🚫 هذا المستخدم محظور."
        )
        return

    try:
        bot.copy_message(
            chat_id=user_id,
            from_chat_id=message.chat.id,
            message_id=message.message_id
        )

        bot.send_message(
            ADMIN_ID,
            "✅ تم إرسال الرد للمستخدم."
        )

    except Exception as error:
        bot.send_message(
            ADMIN_ID,
            f"❌ فشل إرسال الرسالة:\n{error}"
        )
        @bot.message_handler(commands=["users"])
def users_command(message):

    if message.from_user.id != ADMIN_ID:
        return

    db = load_users()

    user_ids = set(db.values())

    bot.send_message(
        ADMIN_ID,
        f"👥 عدد المستخدمين: {len(user_ids)}"
    )


@bot.message_handler(commands=["ban"])
def ban_command(message):

    if message.from_user.id != ADMIN_ID:
        return

    parts = message.text.split()

    if len(parts) != 2:
        bot.reply_to(
            message,
            "الاستخدام:\n/ban USER_ID"
        )
        return

    try:
        user_id = int(parts[1])
    except ValueError:
        bot.reply_to(message, "❌ ID غير صحيح.")
        return

    banned = load_banned()

    if user_id not in banned:
        banned.append(user_id)
        save_banned(banned)

    bot.reply_to(
        message,
        f"🚫 تم حظر المستخدم:\n{user_id}"
    )


@bot.message_handler(commands=["unban"])
def unban_command(message):

    if message.from_user.id != ADMIN_ID:
        return

    parts = message.text.split()

    if len(parts) != 2:
        bot.reply_to(
            message,
            "الاستخدام:\n/unban USER_ID"
        )
        return

    try:
        user_id = int(parts[1])
    except ValueError:
        bot.reply_to(message, "❌ ID غير صحيح.")
        return

    banned = load_banned()

    if user_id in banned:
        banned.remove(user_id)
        save_banned(banned)

        bot.reply_to(
            message,
            f"✅ تم إلغاء حظر المستخدم:\n{user_id}"
        )
    else:
        bot.reply_to(
            message,
            "هذا المستخدم غير محظور."
        )
        @bot.message_handler(commands=["broadcast"])
def broadcast_command(message):

    if message.from_user.id != ADMIN_ID:
        return

    if not message.reply_to_message:
        bot.reply_to(
            message,
            "استخدم الأمر بالرد على رسالة:\n"
            "/broadcast"
        )
        return

    db = load_users()
    user_ids = set(db.values())

    success = 0
    failed = 0

    for user_id in user_ids:
        try:
            bot.copy_message(
                chat_id=user_id,
                from_chat_id=message.chat.id,
                message_id=message.reply_to_message.message_id
            )
            success += 1

        except Exception:
            failed += 1

    bot.send_message(
        ADMIN_ID,
        f"📢 اكتملت الإذاعة.\n\n"
        f"✅ تم الإرسال: {success}\n"
        f"❌ فشل الإرسال: {failed}"
    )
    print("Bot Started")

bot.infinity_polling(
    skip_pending=True
)
