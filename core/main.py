import os
import telebot
from telebot import apihelper
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
import json
import logging
import sqlite3
from telebot.types import InlineQueryResultArticle, InputTextMessageContent

# Connecting to sqlite3
conn = sqlite3.connect('files.db')
cursor = conn.cursor()
# apihelper.ENABLE_MIDDLEWARE = True

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

load_dotenv()

API_TOKEN = os.environ.get("API_TOKEN")
if API_TOKEN is None:
    raise ValueError("API_TOKEN is not set in environment variables")

bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    print(f"Received message from {message.from_user.username}: {message.text}")

@bot.message_handler(commands=['hello'])
def greet_user(message):
    bot.reply_to(message, "Hello! How can I assist you today?")

bot.infinity_polling()
