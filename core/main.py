import os
import telebot
from dotenv import load_dotenv


load_dotenv()

API_TOKEN = os.environ.get("API_TOKEN")
if API_TOKEN is None:
    raise ValueError("API_TOKEN is not set in environment variables")

bot = telebot.TeleBot(API_TOKEN)

bot.infinity_polling()
