import os
import telebot
from telebot import apihelper
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
import json
import logging

apihelper.ENABLE_MIDDLEWARE = True

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

load_dotenv()

API_TOKEN = os.environ.get("API_TOKEN")
if API_TOKEN is None:
    raise ValueError("API_TOKEN is not set in environment variables")

bot = telebot.TeleBot(API_TOKEN)

# Handle '/start' and '/help'
@bot.message_handler(commands=['start'])
def send_welcome(message):
    logger.info("triggered welcome") 
    # markup = ReplyKeyboardMarkup(resize_keyboard=True, input_field_placeholder="Choose you option", one_time_keyboard=True)
    # markup.add(KeyboardButton('help'), KeyboardButton('about'))
    markup = InlineKeyboardMarkup()

    button_google = InlineKeyboardButton("google", url="https://google.com")
    button_youtube = InlineKeyboardButton("youtube", url="https://youtube.com")
    button_step1 = InlineKeyboardButton("step1", callback_data="step1")

    markup.add(button_google)
    markup.add(button_youtube)
    markup.add(button_step1)
    
    bot.send_message(
        message.chat.id,
        "Hi This is a test", reply_markup=markup)
    
@bot.callback_query_handler(func=lambda call: True)
def reply_call(call):
    if call.data == "step1":
        markup = InlineKeyboardMarkup()
        button_step2 = InlineKeyboardButton("step2", callback_data="step2")
        button_cancel = InlineKeyboardButton("cancel", callback_data="cancel")
        markup.add(button_step2, button_cancel)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Choose your next step",
            reply_markup=markup
        )

    if call.data == "step2":
        bot.send_message(call.message.chat.id, "Done")

    if call.data == "cancel":
        bot.answer_callback_query(call.id, "The process has been cancelled", show_alert=True)

    
# @bot.message_handler(func = lambda message: message.text == "about")
# def send_about(message):
#     bot.send_message(message.chat.id, """We are a very powerfull company""")

# @bot.message_handler(func = lambda message: message.text == "help")
# def send_help(message):
#     bot.send_message(message.chat.id, """What is wrong my friend?""")
    
# Handles all sent documents and audio files
# @bot.message_handler(content_types=['document', 'audio'])
# def handle_docs_audio(message):
#     if message.content_type == "document":
#         print("It's a document")
#     elif message.content_type == "audio":
#         print("It's an audio")

# # Handles all text messages that match the regular expression
# @bot.message_handler(regexp="ali")
# def handle_message(message):
# 	print("hi")
     
# def check_hello(message):
#     return message.text == "hello"

# @bot.message_handler(func=check_hello)
# def handle_hello_message(message):
#     print("Triggered")

# @bot.edited_message_handler(func=lambda message:True)
# def handle_edited_message(message):
#     print("edited message is received")

# @bot.message_handler(commands=['setname'])
# def setup_name(message):
#     bot.send_message(message.chat.id, "Please send me your name.")
#     bot.register_next_step_handler(message, callback=assign_first_name)

# def assign_first_name(message, *args, **kwargs):
#     first_name = message.text
#     bot.send_message(message.chat.id, "What is your last name?")
#     bot.register_next_step_handler(message, callback=assign_last_name, first_name=first_name)

# def assign_last_name(message, first_name):
#     last_name = message.text
#     bot.send_message(message.chat.id, f"Your full name is {first_name} {last_name}.")

bot.infinity_polling()
