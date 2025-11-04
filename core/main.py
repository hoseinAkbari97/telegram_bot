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

# Handle '/start' and '/help'
@bot.message_handler(commands=['start'])
def send_welcome(message):
    logger.info("triggered welcome") 
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

@bot.message_handler(commands=['upload_test'])
def send_document_file(message):
    bot.send_chat_action(message.chat.id, action="upload_document")
    bot.send_document(message.chat.id, "BQACAgQAAxkBAAIBv2j3MNSv2mOPBoJnRbM71tCaHfPHAALAJwAC-8-4U1nOUn_ztISPNgQ")
    
@bot.message_handler(content_types=["document", "audio", "voice", "video", "photo"])
def check_id(message):
    logger.info(message.__dict__)
    
@bot.inline_handler(func=lambda query:True)
def query_handler(query):
    logger.info(query)
    results = []
    
    results.append(
        InlineQueryResultArticle(
            id='1',
            title='This is a test',
            input_message_content=InputTextMessageContent(message_text='This is the main response'),
            description='This is a description'
        )
    )
    
@bot.inline_handler(func=lambda query:True)
def query_handler(query):
    logger.info(query)
    results = []
    
    results.append(
        InlineQueryResultArticle(
            id='2',
            title='Join the Bot',
            input_message_content=InputTextMessageContent(message_text='Join the bot'),
            url='https://t.me/cando_helper_bot'
        )
    )
    
    bot.answer_inline_query(query.id, results, cache_time=0)

bot.infinity_polling()
