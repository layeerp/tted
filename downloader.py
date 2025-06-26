
import yt_dlp
from config import MAX_DURATION, AUDIO_QUALITY
from pathlib import Path
import time
import os
import asyncio

TEMP = Path("temp")
DOWNLOADS = Path("downloads")
for p in [TEMP, DOWNLOADS]: p.mkdir(exist_ok=True)

class MusicDownloader:
    def __init__(self):
        self.queue = set()

    def is_user_busy(self, uid): return uid in self.queue
    def set_user_busy(self, uid): self.queue.add(uid)
    def clear_user(self, uid): self.queue.discard(uid)

    async def download(self, query, uid):
        filename_base = f"audio_{uid}_{int(time.time())}"
        opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'noplaylist': True,
            'outtmpl': str(TEMP / f"{filename_base}.%(ext)s"),
            'match_filter': lambda info: "too long" if info.get('duration', 0) > MAX_DURATION else None,
            'sleep_interval': 1,
            'max_sleep_interval': 3,
            'retries': 3,
        }
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                # تحميل مباشر بدون تأخير إضافي
                info = ydl.extract_info(f"ytsearch1:{query}", download=True)
                if 'entries' in info:
                    info = info['entries'][0]
            
            # Find the downloaded file with its actual extension
            for file in TEMP.glob(f"{filename_base}.*"):
                if file.suffix in ['.m4a', '.webm', '.mp4', '.opus']:
                    final = DOWNLOADS / file.name
                    file.rename(final)
                    return {
                        'file_path': final,
                        'title': info.get('title', 'Unknown'),
                        'artist': info.get('uploader', 'Unknown'),
                        'duration': info.get('duration', 0)
                    }
            
            print(f"No audio file found with base name: {filename_base}")
            return None
        except Exception as e:
            print(f"Download error: {e}")
            return None

def clean_old_files(hours=12):
    now = time.time()
    for folder in [TEMP, DOWNLOADS]:
        for ext in ["*.mp3", "*.m4a", "*.webm", "*.mp4", "*.opus"]:
            for file in folder.glob(ext):
                if now - file.stat().st_mtime > hours * 3600:
                    try: file.unlink()
                    except: pass
