from telegram.ext import CommandHandler, MessageHandler, filters
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from downloader import MusicDownloader
from templates import WELCOME, NOT_FOUND, WAIT
from utils import detect_language, is_valid_query

downloader = MusicDownloader()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = detect_language(update.effective_user.language_code)
    await update.message.reply_text(WELCOME[lang], parse_mode='Markdown')

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = detect_language(update.effective_user.language_code)
    query = ' '.join(context.args or [])
    if not is_valid_query(query):
        await update.message.reply_text(NOT_FOUND[lang])
        return
    await process_download(update, user_id, lang, query)

async def text_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = detect_language(update.effective_user.language_code)
    text = update.message.text.strip()

    if update.message.chat.type in ['group', 'supergroup']:
        bot_username = context.bot.username

        if (update.message.reply_to_message and 
            update.message.reply_to_message.from_user and
            update.message.reply_to_message.from_user.username == bot_username):
            query = text.strip()
            if is_valid_query(query):
                await process_download(update, user_id, lang, query)
            else:
                await update.message.reply_text(NOT_FOUND[lang])
            return

        if f"@{bot_username}" in text:
            query = text.replace(f"@{bot_username}", "").strip()
            if is_valid_query(query):
                await process_download(update, user_id, lang, query)
            else:
                await update.message.reply_text(NOT_FOUND[lang])
            return

        if text.lower().startswith('search '):
            query = text[7:].strip()
            if is_valid_query(query):
                await process_download(update, user_id, lang, query)
            else:
                await update.message.reply_text(NOT_FOUND[lang])
        return

    if is_valid_query(text):
        await process_download(update, user_id, lang, text)
    else:
        await update.message.reply_text(NOT_FOUND[lang])

async def process_download(update: Update, user_id: int, lang: str, query: str):
    if downloader.is_user_busy(user_id):
        await update.message.reply_text(WAIT[lang])
        return

    downloader.set_user_busy(user_id)
    msg = await update.message.reply_text("⏳ Searching...")

    try:
        result = await downloader.download(query, user_id)
        if result:
            await msg.edit_text("⏬ Uploading...")

            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("T_7_P", url="https://t.me/T_7_P")]
            ])

            with open(result['file_path'], 'rb') as audio_file:
                await update.message.reply_audio(
                    audio=audio_file,
                    title=result['title'],
                    performer=result['artist'],
                    duration=result['duration'],
                    reply_markup=keyboard,
                    write_timeout=60,
                    read_timeout=60
                )
            await msg.delete()
        else:
            await msg.edit_text(NOT_FOUND[lang])
    finally:
        downloader.clear_user(user_id)

def setup_handlers(app):
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler(["search", "srch"], search))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_search))