import os
import telebot
from telebot import apihelper
from dotenv import load_dotenv
import json
import logging

apihelper.ENABLE_MIDDLEWARE = True

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

# This is a test


load_dotenv()

API_TOKEN = os.environ.get("API_TOKEN")
if API_TOKEN is None:
    raise ValueError("API_TOKEN is not set in environment variables")

bot = telebot.TeleBot(API_TOKEN)

# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    logger.info("triggered welcome") 
    bot.send_message(
        message.chat.id,
        json.dumps(message.chat.__dict__, indent=4, ensure_ascii=False))
    


@bot.middleware_handler(update_types=['message'])
def modify_message(bot_instance, message):
    print("Middleware triggered")
    # You can modify the message object here if needed
    message.another_text = ":changed by middleware"

@bot.message_handler(func=lambda message: True)
def reply_modified_message(message):
    bot.reply_to(message, message.another_text)

# Handles all sent documents and audio files
@bot.message_handler(content_types=['document', 'audio'])
def handle_docs_audio(message):
    if message.content_type == "document":
        print("It's a document")
    elif message.content_type == "audio":
        print("It's an audio")

# Handles all text messages that match the regular expression
@bot.message_handler(regexp="ali")
def handle_message(message):
	print("hi")
     
def check_hello(message):
    return message.text == "hello"

@bot.message_handler(func=check_hello)
def handle_hello_message(message):
    print("Triggered")

@bot.edited_message_handler(func=lambda message:True)
def handle_edited_message(message):
    print("edited message is received")

bot.infinity_polling()
