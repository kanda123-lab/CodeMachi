from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from db import upsert_user, set_mode, get_mode


MODE_KEYBOARD = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("🔀 Tanglish", callback_data="mode_tanglish"),
        InlineKeyboardButton("🟢 Tamil", callback_data="mode_tamil"),
        InlineKeyboardButton("🔵 English", callback_data="mode_english"),
    ]
])

QUICK_ACTIONS_KEYBOARD = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("🔁 Language", callback_data="show_mode"),
        InlineKeyboardButton("🎯 Topic", callback_data="show_topic"),
    ],
    [
        InlineKeyboardButton("📚 Learn", callback_data="show_learn"),
        InlineKeyboardButton("📊 Usage", callback_data="show_usage"),
    ],
])


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    upsert_user(user_id)

    await update.message.reply_text(
        "👋 Vanakam! I'm *CodeMachi* — your AI buddy!\n\n"
        "I can help with *Code*, *Medical*, *Sports*, or *General* topics — "
        "in Tanglish, Tamil, or English.\n\n"
        "First, pick your language style:",
        parse_mode="Markdown",
        reply_markup=MODE_KEYBOARD,
    )


async def mode_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    upsert_user(user_id)
    current = get_mode(user_id)

    mode_labels = {"tanglish": "🔀 Tanglish", "tamil": "🟢 Tamil", "english": "🔵 English"}
    current_label = mode_labels.get(current, current)

    await update.message.reply_text(
        f"Current mode: *{current_label}*\n\nChange to:",
        parse_mode="Markdown",
        reply_markup=MODE_KEYBOARD,
    )


async def mode_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    user_id = query.from_user.id

    if data == "show_mode":
        current = get_mode(user_id)
        mode_labels = {"tanglish": "🔀 Tanglish", "tamil": "🟢 Tamil", "english": "🔵 English"}
        await query.message.reply_text(
            f"Current mode: *{mode_labels.get(current, current)}*\n\nChange to:",
            parse_mode="Markdown",
            reply_markup=MODE_KEYBOARD,
        )
        return

    if not data.startswith("mode_"):
        return

    mode = data.replace("mode_", "")
    set_mode(user_id, mode)

    confirmations = {
        "tanglish": "🔀 Tanglish mode set! Ipo naan Tanglish la pesuvom, bro.",
        "tamil": "🟢 Tamil mode set! இனி தமிழில் பேசலாம்.",
        "english": "🔵 English mode set! Let's go.",
    }
    await query.edit_message_text(confirmations.get(mode, "Mode updated!"))
