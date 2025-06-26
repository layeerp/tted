
from telegram.ext import Application
from config import BOT_TOKEN
from handlers import setup_handlers
from downloader import clean_old_files
import threading
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return "✅ Bot is running"

def run_flask():
    app.run(host='0.0.0.0', port=5000)

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    setup_handlers(application)
    threading.Thread(target=run_flask, daemon=True).start()
    application.run_polling()

if __name__ == '__main__':
    main()
