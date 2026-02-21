import os
import yt_dlp
import asyncio
import logging
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- RENDER အတွက် WEB SERVER ပိုင်း (မပါရင် Error တက်ပါလိမ့်မယ်) ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is Running!")

def run_health_check_server():
    # Render က ပေးတဲ့ PORT ကို သုံးပါမယ် (မရှိရင် 8080)
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    print(f"🌍 Web server started on port {port}")
    server.serve_forever()

# --- BOT ရဲ့ လုပ်ဆောင်ချက်ပိုင်း ---
TOKEN = '7687553839:AAEKB2101j5G_glMEbjYsUMbJ9M4z2tLZM8'

async def download_and_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    chat_id = update.message.chat_id
    
    if "youtube.com" not in url and "youtu.be" not in url:
        await update.message.reply_text("⚠️ YouTube Link ပို့ပေးပါဗျာ။")
        return

    status_msg = await update.message.reply_text("⏳ ဒေါင်းလုပ်ဆွဲနေပါပြီ... ခဏစောင့်ပါ။")
    filename = f"video_{chat_id}.mp4"
    
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': filename,
        'max_filesize': 45 * 1024 * 1024,
        'quiet': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            await asyncio.to_thread(ydl.download, [url])
        
        await status_msg.edit_text("📤 Telegram သို့ တင်ပေးနေပါပြီ...")
        
        with open(filename, 'rb') as video_file:
            await update.message.reply_video(
                video=video_file, 
                caption="✅ Done! (Hosted on Render)",
                connect_timeout=300,
                write_timeout=300
            )
            
        if os.path.exists(filename):
            os.remove(filename)
        await status_msg.delete()

    except Exception as e:
        await status_msg.edit_text(f"❌ Error: {str(e)}")
        if os.path.exists(filename):
            os.remove(filename)

def main():
    # Render အတွက် Web Server ကို Thread တစ်ခုနဲ့ သီးသန့် Run ထားပါမယ်
    web_thread = threading.Thread(target=run_health_check_server, daemon=True)
    web_thread.start()

    # Telegram Bot ကို စတင်ပါမယ်
    print("🤖 Bot is starting on Render Free Web Service...")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_and_send))
    
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()

