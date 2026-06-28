import logging
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from db import init_db
from handlers.start import start_handler, mode_handler, mode_callback
from handlers.chat import message_handler
from handlers.usage import usage_handler, usage_callback
from handlers.learn import learn_handler, learn_callback
from handlers.topic import topic_handler, topic_callback

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler("codemachi.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN not set in environment")

    init_db()
    logger.info("Database initialised")

    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("mode", mode_handler))
    app.add_handler(CommandHandler("topic", topic_handler))
    app.add_handler(CommandHandler("usage", usage_handler))
    app.add_handler(CommandHandler("learn", learn_handler))

    app.add_handler(CallbackQueryHandler(mode_callback, pattern="^mode_"))
    app.add_handler(CallbackQueryHandler(mode_callback, pattern="^show_mode$"))
    app.add_handler(CallbackQueryHandler(topic_callback, pattern="^topic_"))
    app.add_handler(CallbackQueryHandler(topic_callback, pattern="^show_topic$"))
    app.add_handler(CallbackQueryHandler(learn_callback, pattern="^learn_"))
    app.add_handler(CallbackQueryHandler(learn_callback, pattern="^show_learn$"))
    app.add_handler(CallbackQueryHandler(usage_callback, pattern="^show_usage$"))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    logger.info("CodeMachi bot starting (polling)...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
