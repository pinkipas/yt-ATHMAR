from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from docx import Document
from fpdf import FPDF
import os

TOKEN = "8334910114:AAGFjoBXLi3XF1hT8DTeXjEmwie2yKJXt7c"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me a Word file (.docx), and I will convert it to PDF!")

async def convert_word_to_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.document:
        await update.message.reply_text("Please send a Word (.docx) file.")
        return

    file = update.message.document
    if not file.file_name.endswith(".docx"):
        await update.message.reply_text("Only .docx files are supported.")
        return

    file_path = f"temp_{file.file_name}"
    await file.get_file().download_to_drive(file_path)

    doc = Document(file_path)
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            pdf.multi_cell(0, 10, text)

    pdf_path = file_path.replace(".docx", ".pdf")
    pdf.output(pdf_path)

    await update.message.reply_document(document=open(pdf_path, "rb"))

    os.remove(file_path)
    os.remove(pdf_path)

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, convert_word_to_pdf))
    print("🚀 Bot is running...")
    app.run_polling()  # <-- Do NOT use asyncio.run() here

if __name__ == "__main__":
    main()
