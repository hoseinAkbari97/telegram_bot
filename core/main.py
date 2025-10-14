import os
import telebot
from telebot import apihelper
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
import json
import logging

# apihelper.ENABLE_MIDDLEWARE = True

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
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="You are goorba"
            )

    if call.data == "cancel":
        bot.answer_callback_query(call.id, "The process has been cancelled", show_alert=True)
        bot.delete_message(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            timeout=5
        )

@bot.message_handler(commands=['test_voice'])
def send_voice_file(message):
    voice_file = open("./docs/test/files/test.mp3", "rb")
    bot.send_chat_action(message.chat.id, action="upload_voice")
    bot.send_voice(message.chat.id, voice_file)

bot.infinity_polling()
