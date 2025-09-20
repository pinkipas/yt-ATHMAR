import logging
import requests
import base64
import json
import asyncio
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- Configuration ---
# You must get these tokens and keys from their respective platforms
# 1. Telegram Bot Token: Go to @BotFather on Telegram and create a new bot.
# 2. Gemini API Key: Get this from Google AI Studio. Make sure to enable the necessary APIs.
YOUR_TELEGRAM_BOT_TOKEN = "8305596005:AAEBWYylaphXzNzIqvs8wEHtaAA3waHIpCs"
YOUR_GEMINI_API_KEY = "AIzaSyBQ7ISVMmJfu7xu2Y-4qFTYn_igfuWcKLM"

# --- Setup Logging ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# --- Gemini API Constants ---
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict"
GEMINI_API_HEADERS = {
    "Content-Type": "application/json",
}

# --- Bot Command Handlers ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message when the command /start is issued."""
    await update.message.reply_text(
        "Hello! I am an image generation bot powered by the Gemini API. "
        "Send me a description of the image you want to create, and I will generate it for you."
    )

async def generate_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles a user's text message, sends the prompt to the Gemini API,
    and replies with the generated image.
    """
    user_prompt = update.message.text
    if not user_prompt:
        await update.message.reply_text("Please provide a text description to generate an image.")
        return

    await update.message.reply_text("Generating your image... This may take a moment.")
    logger.info(f"Received prompt from user {update.effective_user.id}: '{user_prompt}'")

    try:
        # Construct the payload for the Gemini API
        payload = {
            "instances": {
                "prompt": user_prompt
            },
            "parameters": {
                "sampleCount": 1
            }
        }
        
        # Add the API key as a query parameter
        params = {"key": YOUR_GEMINI_API_KEY}

        # Make the API call to generate the image
        response = requests.post(
            GEMINI_API_URL,
            headers=GEMINI_API_HEADERS,
            json=payload,
            params=params
        )
        response.raise_for_status()

        # Parse the response and extract the Base64 image data
        response_data = response.json()
        if 'predictions' in response_data and len(response_data['predictions']) > 0:
            base64_data = response_data['predictions'][0].get('bytesBase64Encoded')
            if base64_data:
                # Decode the Base64 data to get the raw image bytes
                image_bytes = base64.b64decode(base64_data)
                
                # Send the photo back to the user
                await update.message.reply_photo(photo=image_bytes, caption=f"Prompt: {user_prompt}")
                logger.info("Successfully sent image to user.")
            else:
                await update.message.reply_text("Could not find image data in the API response.")
                logger.error("No Base64 data found in API response.")
        else:
            await update.message.reply_text("The API did not return a valid image.")
            logger.error(f"API response missing predictions: {response_data}")

    except requests.exceptions.HTTPError as http_err:
        error_message = f"HTTP error occurred: {http_err.response.text}"
        await update.message.reply_text(f"An API error occurred: {error_message}")
        logger.error(error_message)
    except Exception as e:
        await update.message.reply_text("An unexpected error occurred while generating the image.")
        logger.error(f"An unexpected error occurred: {e}")

# --- Main Function to Run the Bot ---

def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(YOUR_TELEGRAM_BOT_TOKEN).build()

    # Add command and message handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate_image))

    # Run the bot until the user presses Ctrl-C
    logger.info("Bot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
