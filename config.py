
import os
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
MAX_DURATION = int(os.getenv("MAX_DURATION", 600))
AUDIO_QUALITY = os.getenv("AUDIO_QUALITY", "128")
