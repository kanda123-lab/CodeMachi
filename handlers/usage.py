from telegram import Update
from telegram.ext import ContextTypes
from db import get_usage, get_mode, upsert_user


USAGE_MESSAGES = {
    "tanglish": {
        "pro": "🌟 Bro, nee Pro user! Unlimited questions padicko.",
        "free": (
            "📊 Indha naaikku unoda usage:\n\n"
            "✅ Use pannina: {count}/5\n"
            "🔋 Remaining: {remaining} questions\n\n"
            "{status}"
        ),
        "plenty": "Nalla iruku, indha naaikku innum questions irukkு!",
        "low": "Kekkaradha kekkudan — questions kumaiya use pannu bro.",
        "empty": "Indha naaikku questions mudinjiruchu 😅 Naalaikku reset aagum.",
    },
    "tamil": {
        "pro": "🌟 நீங்கள் Pro user! எல்லா கேள்விகளும் கேளுங்கள்.",
        "free": (
            "📊 இன்றைய பயன்பாடு:\n\n"
            "✅ பயன்படுத்தியது: {count}/5\n"
            "🔋 மீதமுள்ளது: {remaining} கேள்விகள்\n\n"
            "{status}"
        ),
        "plenty": "நல்லது! இன்னும் கேள்விகள் உள்ளன.",
        "low": "கவனமாக கேளுங்கள் — சில கேள்விகளே மீதமுள்ளன.",
        "empty": "இன்றைய கேள்விகள் முடிந்துவிட்டன 😅 நாளை மீண்டும் கிடைக்கும்.",
    },
    "english": {
        "pro": "🌟 You're on Pro — ask away, no limits!",
        "free": (
            "📊 Your usage today:\n\n"
            "✅ Used: {count}/5\n"
            "🔋 Remaining: {remaining} questions\n\n"
            "{status}"
        ),
        "plenty": "You've got plenty left for today!",
        "low": "Getting close — use them wisely.",
        "empty": "You've hit today's limit 😅 Resets tomorrow.",
    },
}


async def usage_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    upsert_user(user_id)

    mode = get_mode(user_id)
    msgs = USAGE_MESSAGES.get(mode, USAGE_MESSAGES["english"])
    data = get_usage(user_id)

    if data["is_pro"]:
        await update.message.reply_text(msgs["pro"])
        return

    if data["remaining"] == 0:
        status = msgs["empty"]
    elif data["remaining"] <= 2:
        status = msgs["low"]
    else:
        status = msgs["plenty"]

    text = msgs["free"].format(count=data["count"], remaining=data["remaining"], status=status)
    await update.message.reply_text(text)


async def usage_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    upsert_user(user_id)

    mode = get_mode(user_id)
    msgs = USAGE_MESSAGES.get(mode, USAGE_MESSAGES["english"])
    data = get_usage(user_id)

    if data["is_pro"]:
        await query.message.reply_text(msgs["pro"])
        return

    if data["remaining"] == 0:
        status = msgs["empty"]
    elif data["remaining"] <= 2:
        status = msgs["low"]
    else:
        status = msgs["plenty"]

    text = msgs["free"].format(count=data["count"], remaining=data["remaining"], status=status)
    await query.message.reply_text(text)
