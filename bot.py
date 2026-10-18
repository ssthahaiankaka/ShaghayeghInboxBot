import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.environ["BOT_TOKEN"]
ADMIN_ID = int(os.environ["ADMIN_ID"])

bot = telebot.TeleBot(TOKEN)
senders = {}

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "💗 به ربات پیام ناشناس شقایق خوش اومدی!\n\n"
        "💌 پیامت رو بفرست تا به شقایق برسه.\n\n"
        "🔒 پیام برای دیگران ناشناسه، اما مدیر ربات "
        "می‌تونه شناسه تلگرام فرستنده رو ببینه."
    )

@bot.message_handler(func=lambda m: m.chat.id == ADMIN_ID and
                     m.reply_to_message is not None,
                     content_types=["text", "photo", "video", "voice"])
def reply_to_sender(message):
    original = message.reply_to_message.message_id
    user_id = senders.get(original)

    if not user_id:
        bot.reply_to(message, "فرستنده این پیام پیدا نشد.")
        return

    try:
        bot.copy_message(user_id, ADMIN_ID, message.message_id)
        bot.reply_to(message, "✅ جوابت ارسال شد.")
    except Exception:
        bot.reply_to(message, "❌ ارسال جواب ممکن نشد.")

@bot.message_handler(content_types=["text", "photo", "video", "voice"])
def receive(message):
    if message.chat.id == ADMIN_ID:
        return

    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(
            "🔍 نمایش آیدی فرستنده",
            callback_data=f"id_{message.from_user.id}"
        )
    )

    sent = bot.send_message(
        ADMIN_ID,
        "💌 پیام ناشناس جدید!\n"
        "برای پاسخ، روی پیام دریافتی ریپلای کن.",
        reply_markup=keyboard
    )

    copied = bot.copy_message(
        ADMIN_ID, message.chat.id, message.message_id
    )

    senders[sent.message_id] = message.from_user.id
    senders[copied.message_id] = message.from_user.id

    bot.reply_to(message, "✅ پیامت به شقایق رسید!")

@bot.callback_query_handler(func=lambda call: call.data.startswith("id_"))
def show_id(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "اجازه دسترسی نداری.")
        return

    user_id = int(call.data.split("_")[1])

    try:
        user = bot.get_chat(user_id)
        username = f"@{user.username}" if user.username else "ندارد"
        info = f"شناسه عددی: {user_id}\nیوزرنیم: {username}"
    except Exception:
        info = f"شناسه عددی: {user_id}"

    bot.answer_callback_query(call.id, info, show_alert=True)

bot.infinity_polling()
