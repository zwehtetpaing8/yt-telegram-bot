import os
import yt_dlp
import asyncio
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# Logging setup - Error တွေကို Log မှာ သေချာကြည့်နိုင်အောင်ပါ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)

# သင့်ရဲ့ Bot Token
TOKEN = '7687553839:AAEKB2101j5G_glMEbjYsUMbJ9M4z2tLZM8'

async def download_and_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    chat_id = update.message.chat_id
    
    if "youtube.com" not in url and "youtu.be" not in url:
        await update.message.reply_text("⚠️ YouTube Link ပို့ပေးပါဗျာ။")
        return

    status_msg = await update.message.reply_text("⏳ PythonAnywhere ကနေ ဒေါင်းနေပါပြီ... ခဏစောင့်ပါ။")

    # PythonAnywhere storage မပြည့်အောင် နာမည်ကို Chat ID နဲ့ ပေးပါမယ်
    filename = f"video_{chat_id}.mp4"
    
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': filename,
        'max_filesize': 45 * 1024 * 1024, # 45MB (Free account storage သက်သာအောင်)
        'quiet': True,
        'no_warnings': True
    }

    try:
        # YouTube ဒေါင်းလုပ်ဆွဲခြင်း
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            await asyncio.to_thread(ydl.download, [url])
        
        await status_msg.edit_text(" ဒေါင်းလုပ်ပြီးပါပြီ။ Telegram ဆီ တင်ပေးနေပါပြီ...")
        
        # Telegram ဆီ ဗီဒီယို ပို့ခြင်း
        with open(filename, 'rb') as video_file:
            await update.message.reply_video(
                video=video_file, 
                caption="✅ Downloaded via PythonAnywhere!",
                connect_timeout=300,
                write_timeout=300
            )
            
        # File ကို ချက်ချင်းပြန်ဖျက်ခြင်း (Storage limit မကျော်အောင်)
        if os.path.exists(filename):
            os.remove(filename)
        await status_msg.delete()

    except Exception as e:
        await status_msg.edit_text(f"❌ Error: {str(e)}")
        if os.path.exists(filename):
            os.remove(filename)

def main():
    print("🤖 PythonAnywhere Bot is starting...")
    
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_and_send))
    
    print("✅ Bot is running! Telegram မှာ စမ်းကြည့်နိုင်ပါပြီ။")
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
