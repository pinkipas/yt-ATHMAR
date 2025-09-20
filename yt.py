import os
from docx2pdf import convert
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

TOKEN = "8334910114:AAGFjoBXLi3XF1hT8DTeXjEmwie2yKJXt7c"  # <-- replace with your bot token

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Send me a .docx file and I will convert it to PDF."
    )

# Handle Word documents
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = update.message.document
    if not file.file_name.endswith(".docx"):
        await update.message.reply_text("Please send a .docx file.")
        return

    file_path = file.file_name

    # Download the file
    tg_file = await file.get_file()  # await get_file
    await tg_file.download_to_drive(file_path)  # then download

    # Convert to PDF
    pdf_path = file_path.replace(".docx", ".pdf")
    convert(file_path, pdf_path)

    # Send PDF back
    await update.message.reply_document(document=open(pdf_path, "rb"))

    # Cleanup
    os.remove(file_path)
    os.remove(pdf_path)

# Main function
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.FILE_EXTENSION("docx"), handle_file))

    print("Bot is running...")
    app.run_polling()  # <-- do NOT use asyncio.run() here

if __name__ == "__main__":
    main()
