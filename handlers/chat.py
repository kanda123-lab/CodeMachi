import logging
import anthropic
from telegram import Update
from telegram.ext import ContextTypes
from db import get_mode, check_and_increment_usage, upsert_user
from prompts import PROMPTS, DEFAULT_MODE
from handlers.start import QUICK_ACTIONS_KEYBOARD

logger = logging.getLogger(__name__)

LIMIT_MESSAGES = {
    "tanglish": (
        "Bro, indha naaikku unoda free questions mudinjiruchu 😅\n\n"
        "5 questions per day free la kudukrom. Naalaikku reset aagum!\n\n"
        "More questions vendum-na, Pro plan check pannunga 👉 /upgrade"
    ),
    "tamil": (
        "இன்றைக்கான இலவச கேள்விகள் முடிந்துவிட்டன 😅\n\n"
        "நாளை மீண்டும் 5 கேள்விகள் கிடைக்கும்.\n\n"
        "அதிகமான கேள்விகளுக்கு Pro plan பாருங்கள் 👉 /upgrade"
    ),
    "english": (
        "You've used all 5 free questions for today 😅\n\n"
        "Your limit resets tomorrow. For unlimited questions, check out Pro 👉 /upgrade"
    ),
}


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text

    upsert_user(user_id)
    mode = get_mode(user_id)

    usage = check_and_increment_usage(user_id)
    if not usage["allowed"]:
        await update.message.reply_text(LIMIT_MESSAGES.get(mode, LIMIT_MESSAGES["english"]))
        return

    await update.message.chat.send_action("typing")

    try:
        client = anthropic.Anthropic()
        system_prompt = PROMPTS.get(mode, PROMPTS[DEFAULT_MODE])

        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            system=[{"type": "text", "text": system_prompt, "cache_control": {"type": "ephemeral"}}],
            messages=[{"role": "user", "content": user_text}],
        )

        reply = message.content[0].text
        await update.message.reply_text(reply, reply_markup=QUICK_ACTIONS_KEYBOARD)

    except anthropic.APIError as e:
        logger.error("Anthropic API error for user %s: %s", user_id, e)
        await update.message.reply_text(
            "Something went wrong calling the AI. Try again in a moment!"
        )
    except Exception as e:
        logger.error("Unexpected error for user %s: %s", user_id, e)
        await update.message.reply_text("An unexpected error occurred. Please try again.")
