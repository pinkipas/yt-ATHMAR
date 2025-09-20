# This script creates a Telegram bot that can download videos from YouTube.

import os
import threading
import re
import traceback
import telebot
from pytube import YouTube, exceptions
from telebot import types

# --- Configuration ---
# Replace 'YOUR_BOT_TOKEN' with the token you get from BotFather on Telegram.
BOT_TOKEN = '8334910114:AAGFjoBXLi3XF1hT8DTeXjEmwie2yKJXt7c'
if BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
    raise ValueError("Please replace 'YOUR_BOT_TOKEN_HERE' with your actual bot token from BotFather.")

# Initialize the bot with the provided token.
bot = telebot.TeleBot(BOT_TOKEN)

# --- Helper Functions ---

def sanitize_filename(filename):
    """
    Removes invalid characters from a filename to prevent errors.
    """
    return re.sub(r'[^\w\s\-\.]', '_', filename).strip()

def download_and_send_video(message, url):
    """
    Downloads the YouTube video from the given URL and sends it to the user.
    """
    chat_id = message.chat.id
    temp_file_path = None
    try:
        bot.send_message(chat_id, "Analyzing video link...")
        yt = YouTube(url)

        # Get the highest resolution stream with both video and audio,
        # preferring the progressive stream which is a single file.
        video_stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        
        # Fallback to an adaptive stream if a progressive one isn't found.
        if not video_stream:
            bot.send_message(chat_id, "Note: This video does not have a progressive stream. Only the video will be downloaded (no audio).")
            video_stream = yt.streams.filter(adaptive=True, file_extension='mp4', only_video=True).order_by('resolution').desc().first()
        
        if not video_stream:
            bot.send_message(chat_id, "Sorry, a suitable video stream was not found.")
            return

        bot.send_message(chat_id, f"Downloading video: **{yt.title}**...\nThis may take a few moments.", parse_mode='Markdown')
        
        filename = f"{sanitize_filename(yt.title)}.mp4"
        temp_file_path = f"./{filename}"
        
        # Download the video.
        video_stream.download(output_path='.', filename=temp_file_path)

        bot.send_message(chat_id, "Download complete. Sending video...")

        # Open and send the video file.
        with open(temp_file_path, 'rb') as video_file:
            bot.send_document(chat_id, video_file, caption=f"Downloaded from YouTube: **{yt.title}**", parse_mode='Markdown')
        
        bot.send_message(chat_id, "Video sent successfully!")

    except exceptions.RegexMatchError:
        bot.send_message(chat_id, "Invalid YouTube URL. Please send a valid link.")
    except exceptions.VideoUnavailable:
        bot.send_message(chat_id, "Sorry, this video is unavailable or private.")
    except exceptions.AgeRestrictedError:
        bot.send_message(chat_id, "This video is age-restricted and cannot be downloaded.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        # Print the full traceback for detailed debugging information.
        traceback.print_exc()
        bot.send_message(chat_id, "An unexpected error occurred. Please try again.")
    finally:
        # Clean up the downloaded file, if it exists.
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)

# --- Bot Command Handlers ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """
    Responds to the /start command with a welcome message and instructions.
    """
    welcome_message = (
        "Hello! I am a simple bot that can download videos from YouTube.\n\n"
        "Just send me a link to a YouTube video, and I will try to download it for you. "
        "Please note that large videos may take a while to process."
    )
    bot.send_message(message.chat.id, welcome_message)

@bot.message_handler(func=lambda message: True)
def handle_video_link(message):
    """
    Handles incoming messages that are potential YouTube links.
    """
    download_thread = threading.Thread(
        target=download_and_send_video,
        args=(message, message.text)
    )
    download_thread.start()

# --- Main Bot Loop ---
if __name__ == "__main__":
    print("Bot is starting...")
    bot.polling()
