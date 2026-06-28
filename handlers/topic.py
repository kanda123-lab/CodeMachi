from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from db import upsert_user, set_topic, get_topic, get_mode

TOPIC_KEYBOARD = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("💻 Code", callback_data="topic_code"),
        InlineKeyboardButton("🏥 Medical", callback_data="topic_medical"),
    ],
    [
        InlineKeyboardButton("⚽ Sports", callback_data="topic_sports"),
        InlineKeyboardButton("🌍 General", callback_data="topic_general"),
    ],
])

TOPIC_LABELS = {
    "code": "💻 Code",
    "medical": "🏥 Medical",
    "sports": "⚽ Sports",
    "general": "🌍 General",
}

TOPIC_CONFIRMATIONS = {
    "code": {
        "tanglish": "💻 Code mode! Ipo coding questions kekkalam, bro.",
        "tamil": "💻 Code mode! இனி coding கேள்விகள் கேட்கலாம்.",
        "english": "💻 Code mode set! Ask me anything about programming.",
    },
    "medical": {
        "tanglish": "🏥 Medical mode! Health and medicine topics pesa ready bro.",
        "tamil": "🏥 Medical mode! இனி மருத்துவ கேள்விகள் கேட்கலாம்.",
        "english": "🏥 Medical mode set! Ask me about health and medicine.",
    },
    "sports": {
        "tanglish": "⚽ Sports mode! Ipo sports pathi pesa ready bro — cricket, football, everything!",
        "tamil": "⚽ Sports mode! இனி sports கேள்விகள் கேட்கலாம்.",
        "english": "⚽ Sports mode set! Ask me about any sport.",
    },
    "general": {
        "tanglish": "🌍 General mode! Anything-um kekkalam bro — history, science, finance, cooking!",
        "tamil": "🌍 General mode! எதை வேண்டுமானாலும் கேட்கலாம் — வரலாறு, அறிவியல், நிதி!",
        "english": "🌍 General mode set! Ask me about anything — history, science, finance, and more.",
    },
}


async def topic_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    upsert_user(user_id)
    current = get_topic(user_id)
    current_label = TOPIC_LABELS.get(current, current)

    await update.message.reply_text(
        f"Current topic: *{current_label}*\n\nSwitch to:",
        parse_mode="Markdown",
        reply_markup=TOPIC_KEYBOARD,
    )


async def topic_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    user_id = query.from_user.id

    if data == "show_topic":
        current = get_topic(user_id)
        current_label = TOPIC_LABELS.get(current, current)
        await query.message.reply_text(
            f"Current topic: *{current_label}*\n\nSwitch to:",
            parse_mode="Markdown",
            reply_markup=TOPIC_KEYBOARD,
        )
        return

    if not data.startswith("topic_"):
        return

    topic = data.replace("topic_", "")
    set_topic(user_id, topic)
    mode = get_mode(user_id)

    confirmation = (
        TOPIC_CONFIRMATIONS.get(topic, {}).get(mode)
        or TOPIC_CONFIRMATIONS.get(topic, {}).get("english", "Topic updated!")
    )
    await query.edit_message_text(confirmation)
