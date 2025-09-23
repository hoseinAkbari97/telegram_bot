import os
import telebot
from dotenv import load_dotenv
# import pprint
import json
# import mysql.connector


load_dotenv()

# # --- Database connection info from .env ---
# archive_conn_info = {
#     "host": os.getenv("ARCHIVE_HOST"),
#     "user": os.getenv("ARCHIVE_USER"),
#     "password": os.getenv("ARCHIVE_PASSWORD"),
#     "database": os.getenv("ARCHIVE_DB")
# }

# master_conn_info = {
#     "host": os.getenv("MASTER_HOST"),
#     "user": os.getenv("MASTER_USER"),
#     "password": os.getenv("MASTER_PASSWORD"),
#     "database": os.getenv("MASTER_DB")
# }

API_TOKEN = os.environ.get("API_TOKEN")
if API_TOKEN is None:
    raise ValueError("API_TOKEN is not set in environment variables")

bot = telebot.TeleBot(API_TOKEN)

# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
#     bot.reply_to(message, """\
# Hi there, I am EchoBot.
# I am here to echo your kind words back to you. Just say anything nice and I'll say the exact same thing to you!\
# """)
#     pprint.pprint(message.chat.__dict__, width=4)
    bot.send_message(
        message.chat.id,
        json.dumps(message.chat.__dict__, indent=4, ensure_ascii=False))
    
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

# @bot.message_handler(commands=['outbound'])
# def outbound_count(message):
#     conn = None  
#     cursor = None  
#     try:
#         conn = mysql.connector.connect(**master_conn_info)
#         cursor = conn.cursor()
#         cursor.execute("SELECT COUNT(*) FROM outbound_messages")
#         result = cursor.fetchone()
#         count = result if result and result is not None else 0
#         bot.send_message(message.chat.id, f"Total outbound messages: {count}")
#     except mysql.connector.Error as err:
#         bot.send_message(message.chat.id, f"Error: {err}")
#     except IndexError:
#         # Handle the case where fetchone() returns an empty tuple
#         bot.send_message(message.chat.id, f"Error: No count returned from the query.")
#     finally:
#         # These checks will now safely handle the case where the variables were never assigned
#         if cursor:
#             cursor.close()
#         if conn:
#             conn.close()

@bot.message_handler(func=lambda message: True)
def handle_edited_message(message):
    print("edited message is received")

bot.infinity_polling()
