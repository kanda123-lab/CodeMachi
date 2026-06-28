import logging
import anthropic
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from db import get_mode, get_topic, check_and_increment_usage, upsert_user
from prompts import get_prompt
from handlers.start import QUICK_ACTIONS_KEYBOARD

logger = logging.getLogger(__name__)

LEARN_TOPICS = {
    "code": [
        ("🐍", "Python"), ("⚡", "JavaScript"), ("⚛️", "React"), ("🧩", "DSA"),
        ("🗄️", "SQL"), ("🌿", "Git"), ("🟩", "Node.js"), ("🏗️", "System Design"),
    ],
    "medical": [
        ("🫀", "Cardiology"), ("🧠", "Neurology"), ("💊", "Pharmacology"), ("🩺", "Anatomy"),
        ("🏥", "First Aid"), ("🥗", "Nutrition"), ("🧬", "Genetics"), ("🧘", "Mental Health"),
        ("🫘", "Renal Dialysis"), ("🤰", "Obstetrics & Gynecology"),
    ],
    "sports": [
        ("⚽", "Football"), ("🏏", "Cricket"), ("🎾", "Tennis"), ("🏋️", "Fitness"),
        ("🏀", "Basketball"), ("🏊", "Swimming"), ("🚴", "Cycling"), ("🥊", "Boxing"),
    ],
    "general": [
        ("📖", "History"), ("🌍", "Geography"), ("🔭", "Science"), ("🎨", "Art"),
        ("💰", "Finance"), ("🍳", "Cooking"), ("🌐", "Technology"), ("📝", "Writing"),
    ],
}

LEARN_INTRO = {
    "tanglish": "📚 Enna topic learn pannanum? Oru button press pannu:",
    "tamil": "📚 எந்த topic கற்றுக்கொள்ள விரும்புகிறீர்கள்? ஒரு button அழுத்துங்கள்:",
    "english": "📚 What topic do you want to learn? Pick one:",
}


def build_learn_keyboard(topic: str) -> InlineKeyboardMarkup:
    items = LEARN_TOPICS.get(topic, LEARN_TOPICS["code"])
    rows = []
    for i in range(0, len(items), 4):
        row = [
            InlineKeyboardButton(f"{emoji} {name}", callback_data=f"learn_{name}")
            for emoji, name in items[i:i + 4]
        ]
        rows.append(row)
    return InlineKeyboardMarkup(rows)


async def learn_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    upsert_user(user_id)
    mode = get_mode(user_id)
    topic = get_topic(user_id)

    await update.message.reply_text(
        LEARN_INTRO.get(mode, LEARN_INTRO["english"]),
        reply_markup=build_learn_keyboard(topic),
    )


async def learn_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    user_id = query.from_user.id

    if data == "show_learn":
        upsert_user(user_id)
        mode = get_mode(user_id)
        topic = get_topic(user_id)
        await query.message.reply_text(
            LEARN_INTRO.get(mode, LEARN_INTRO["english"]),
            reply_markup=build_learn_keyboard(topic),
        )
        return

    if not data.startswith("learn_"):
        return

    subject = data.replace("learn_", "")
    upsert_user(user_id)
    mode = get_mode(user_id)
    topic = get_topic(user_id)

    usage = check_and_increment_usage(user_id)
    if not usage["allowed"]:
        from handlers.chat import LIMIT_MESSAGES
        await query.message.reply_text(LIMIT_MESSAGES.get(mode, LIMIT_MESSAGES["english"]))
        return

    await query.message.chat.send_action("typing")

    try:
        client = anthropic.Anthropic()
        system_prompt = get_prompt(topic, mode)

        learn_prompt = (
            f"Teach me {subject} from the very basics. "
            "Start with what it is, why it matters, and give me a simple first example with clear explanation."
        )

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
