import logging
import anthropic
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from db import get_mode, check_and_increment_usage, upsert_user
from prompts import PROMPTS, DEFAULT_MODE
from handlers.start import QUICK_ACTIONS_KEYBOARD

logger = logging.getLogger(__name__)

TOPICS = ["Python", "JavaScript", "React", "DSA", "SQL", "Git", "Node.js", "System Design"]

LEARN_KEYBOARD = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("🐍 Python", callback_data="learn_Python"),
        InlineKeyboardButton("⚡ JavaScript", callback_data="learn_JavaScript"),
        InlineKeyboardButton("⚛️ React", callback_data="learn_React"),
        InlineKeyboardButton("🧩 DSA", callback_data="learn_DSA"),
    ],
    [
        InlineKeyboardButton("🗄️ SQL", callback_data="learn_SQL"),
        InlineKeyboardButton("🌿 Git", callback_data="learn_Git"),
        InlineKeyboardButton("🟩 Node.js", callback_data="learn_Node.js"),
        InlineKeyboardButton("🏗️ System Design", callback_data="learn_System Design"),
    ],
])

LEARN_INTRO = {
    "tanglish": "📚 Enna topic learn pannanum? Oru button press pannu:",
    "tamil": "📚 எந்த topic கற்றுக்கொள்ள விரும்புகிறீர்கள்? ஒரு button அழுத்துங்கள்:",
    "english": "📚 What topic do you want to learn? Pick one:",
}


async def learn_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    upsert_user(user_id)
    mode = get_mode(user_id)

    await update.message.reply_text(
        LEARN_INTRO.get(mode, LEARN_INTRO["english"]),
        reply_markup=LEARN_KEYBOARD,
    )


async def learn_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    user_id = query.from_user.id

    if data == "show_learn":
        upsert_user(user_id)
        mode = get_mode(user_id)
        await query.message.reply_text(
            LEARN_INTRO.get(mode, LEARN_INTRO["english"]),
            reply_markup=LEARN_KEYBOARD,
        )
        return

    if not data.startswith("learn_"):
        return

    topic = data.replace("learn_", "")
    upsert_user(user_id)
    mode = get_mode(user_id)

    usage = check_and_increment_usage(user_id)
    if not usage["allowed"]:
        from handlers.chat import LIMIT_MESSAGES
        await query.message.reply_text(LIMIT_MESSAGES.get(mode, LIMIT_MESSAGES["english"]))
        return

    await query.message.chat.send_action("typing")

    try:
        client = anthropic.Anthropic()
        system_prompt = PROMPTS.get(mode, PROMPTS[DEFAULT_MODE])

        learn_prompt = f"Teach me {topic} from the very basics. Start with what it is, why it matters, and show me a simple first example with clear explanation."

        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            system=[{"type": "text", "text": system_prompt, "cache_control": {"type": "ephemeral"}}],
            messages=[{"role": "user", "content": learn_prompt}],
        )

        reply = message.content[0].text
        await query.message.reply_text(reply, reply_markup=QUICK_ACTIONS_KEYBOARD)

    except anthropic.APIError as e:
        logger.error("Anthropic API error in learn for user %s: %s", user_id, e)
        await query.message.reply_text("Something went wrong. Try again in a moment!")
    except Exception as e:
        logger.error("Unexpected error in learn for user %s: %s", user_id, e)
        await query.message.reply_text("An unexpected error occurred. Please try again.")
