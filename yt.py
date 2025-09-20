import os
import asyncio
from pytube import YouTube
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = "YOUR_BOT_TOKEN_HERE"  # Replace with your bot token

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! Send me a YouTube link and I will download the video for you.")

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    await update.message.reply_text("Downloading video... ⏳")

    try:
        yt = YouTube(url)
        stream = yt.streams.get_highest_resolution()
        file_path = os.path.join(DOWNLOAD_FOLDER, f"{yt.title}.mp4")
        stream.download(output_path=DOWNLOAD_FOLDER, filename=f"{yt.title}.mp4")
        
        await update.message.reply_text("Uploading video... ⏳")
        await context.bot.send_video(chat_id=update.effective_chat.id, video=open(file_path, 'rb'))
        os.remove(file_path)  # delete file after sending

    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    print("🚀 Bot is running...")
    asyncio.run(app.run_polling())

if __name__ == "__main__":
    main()
