# This script creates a Telegram bot that converts Word (.docx) and PowerPoint (.pptx) files to PDF.
#
# **Prerequisites:**
# 1.  A Telegram Bot Token from the @BotFather.
# 2.  Python library: `python-telegram-bot`
# 3.  **LibreOffice installed on your system.** This is a critical dependency for the conversion to work.
# 4.  The `libreoffice` executable must be in your system's PATH.
#
# **How to Use:**
# 1.  Install the required Python library: `pip install python-telegram-bot`
# 2.  Install LibreOffice on your operating system.
# 3.  Replace "YOUR_BOT_TOKEN_HERE" with your actual token from @BotFather.
# 4.  Run this script: `python your_script_name.py`
#
# Note: This version uses Python's `subprocess` module to call the LibreOffice command-line tool directly.
# This makes it more robust than relying on a Python wrapper library.

import os
import uuid
import logging
import subprocess
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Configure logging to see what the bot is doing
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Replace with your bot token
BOT_TOKEN = "8305596005:AAEBWYylaphXzNzIqvs8wEHtaAA3waHIpCs"

# Create a temporary directory to store files during conversion
TEMP_DIR = "temp"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

# --- Command Handlers ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Greets the user and explains the bot's purpose."""
    await update.message.reply_text(
        "Hello! I'm a file conversion bot. "
        "Just send me a Word (.docx) or PowerPoint (.pptx) file, "
        "and I will convert it to a PDF for you."
    )

# --- Message Handlers ---

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles incoming documents for conversion."""
    document = update.message.document
    filename = document.file_name

    # Check the file extension to determine if it's a supported format
    file_ext = os.path.splitext(filename)[1].lower()
    if file_ext not in [".docx", ".pptx"]:
        await update.message.reply_text(
            f"Sorry, I can't convert '{file_ext}' files. "
            "Please send a .docx or .pptx file."
        )
        return

    await update.message.reply_text(
        f"Received '{filename}'. Please wait while I convert it to a PDF..."
    )

    # Generate unique filenames to avoid conflicts
    unique_id = uuid.uuid4().hex
    input_path = os.path.join(TEMP_DIR, f"{unique_id}_{filename}")
    output_dir = os.path.join(TEMP_DIR, unique_id)
    os.makedirs(output_dir, exist_ok=True)
    
    # Construct the expected output path for the PDF
    pdf_filename = f"{os.path.splitext(filename)[0]}.pdf"
    output_path = os.path.join(output_dir, pdf_filename)

    try:
        # Download the file to the temp directory
        new_file = await context.bot.get_file(document.file_id)
        await new_file.download_to_drive(input_path)

        # Perform the conversion using the LibreOffice command-line tool
        command = [
            "libreoffice",
            "--headless", # Run without a graphical interface
            "--convert-to",
            "pdf",
            input_path,
            "--outdir",
            output_dir
        ]
        
        # Execute the command and capture the output
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        logging.info(f"LibreOffice conversion output:\n{result.stdout}")
        
        # Check if the output file was created
        if not os.path.exists(output_path):
            raise FileNotFoundError(f"Conversion failed: PDF file not found at {output_path}")

        # Send the converted PDF back to the user
        await update.message.reply_document(
            document=open(output_path, "rb"),
            filename=pdf_filename,
            caption=f"Here is your converted PDF for '{filename}'."
        )

    except subprocess.CalledProcessError as e:
        logging.error(f"LibreOffice command failed with exit code {e.returncode}:\n{e.stderr}")
        await update.message.reply_text(
            "An error occurred during the conversion. "
            "Please ensure LibreOffice is installed and in your system's PATH."
        )
    except Exception as e:
        logging.error(f"Error converting document: {e}")
        await update.message.reply_text(
            "An error occurred during the conversion. "
            "Please try again or check the server logs for more details."
        )
    finally:
        # Clean up temporary files
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)
        if os.path.exists(output_dir):
            os.rmdir(output_dir)

async def handle_unsupported_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles messages that are not documents."""
    await update.message.reply_text(
        "I can only process Word and PowerPoint files. "
        "Please send a document with a .docx or .pptx extension."
    )

# --- Main function to run the bot ---

def main() -> None:
    """Entry point for the bot application."""
    # Create the Application and pass your bot's token.
    application = Application.builder().token(BOT_TOKEN).build()

    # Register the command and message handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    # This handler catches any message that isn't a document
    application.add_handler(MessageHandler(~filters.Document.ALL, handle_unsupported_message))

    # Start the bot
    logging.info("Starting bot...")
    application.run_polling()

if __name__ == "__main__":
    main()
