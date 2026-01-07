import os
import telebot
from telebot import apihelper
from dotenv import load_dotenv
import json
import logging
import sqlite3
import re
import time

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Connecting to sqlite3
conn = sqlite3.connect('files.db')
cursor = conn.cursor()

load_dotenv()

API_TOKEN = os.environ.get("API_TOKEN")
if API_TOKEN is None:
    raise ValueError("API_TOKEN is not set in environment variables")

bot = telebot.TeleBot(API_TOKEN)

# Dictionary to track user message frequency
user_message_count = {}

def is_spam_message(message):
    """Enhanced spam detection function"""
    if not message.text:
        return False
    
    text = message.text.lower()
    
    # Check for common spam patterns
    spam_keywords = ['buy now', 'click here', 'make money', 'earn fast', 
                     'limited offer', 'discount', 'promotion', 'http://', 
                     'https://', 'www.', '.com', '.ru', '.net', '.org',
                     't.me/', '@', 'telegram.me/', 'joinchat']
    
    # Check for excessive CAPS
    if len(message.text) > 10:
        caps_count = sum(1 for c in message.text if c.isupper())
        if caps_count / len(message.text) > 0.7:  # 70% caps
            logger.info(f"SPAM DETECTED - Excessive CAPS: {message.text}")
            return True
    
    # Check for spam keywords
    for keyword in spam_keywords:
        if keyword in text:
            logger.info(f"SPAM DETECTED - Keyword '{keyword}' in: {message.text}")
            return True
    
    # Check for excessive links
    url_pattern = r'(https?://\S+|www\.\S+|t\.me/\S+|telegram\.me/\S+)'
    urls = re.findall(url_pattern, text)
    if len(urls) >= 2:  # More than 2 links
        logger.info(f"SPAM DETECTED - Multiple URLs: {message.text}")
        return True
    
    return False

# ====== CRITICAL: REMOVE THE CATCH-ALL DEBUG HANDLER ======
# It's blocking all other handlers!

# Command handlers - FIRST in order!
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    logger.info(f"COMMAND /start or /help in chat {message.chat.id} ({message.chat.type})")
    bot.reply_to(message, "Hi! I'm an anti-spam bot. Add me to a group and make me admin!")

@bot.message_handler(commands=['hello'])
def greet_user(message):
    logger.info(f"COMMAND /hello in chat {message.chat.id} ({message.chat.type})")
    bot.reply_to(message, "Hello! How can I assist you today?")

@bot.message_handler(commands=['checkperms', 'status'])
def check_permissions(message):
    logger.info(f"COMMAND /checkperms in chat {message.chat.id} ({message.chat.type})")
    try:
        chat_member = bot.get_chat_member(message.chat.id, bot.get_me().id)
        status = chat_member.status
        
        response = f"🤖 **Bot Status Report**\n"
        response += f"Chat ID: `{message.chat.id}`\n"
        response += f"Chat Type: `{message.chat.type}`\n"
        response += f"Chat Title: `{message.chat.title if hasattr(message.chat, 'title') else 'Private Chat'}`\n"
        response += f"Bot Status: `{status}`\n"
        
        if hasattr(chat_member, 'can_delete_messages'):
            response += f"Can delete messages: `{chat_member.can_delete_messages}`\n"
        if hasattr(chat_member, 'can_restrict_members'):
            response += f"Can restrict members: `{chat_member.can_restrict_members}`\n"
        if hasattr(chat_member, 'can_promote_members'):
            response += f"Can promote members: `{chat_member.can_promote_members}`\n"
        
        logger.info(f"Bot permissions in chat {message.chat.id}: {status}")
        bot.reply_to(message, response, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error checking permissions: {str(e)}")
        bot.reply_to(message, f"Error checking permissions: {str(e)}")

@bot.message_handler(commands=['delete'])
def delete_message(message):
    logger.info(f"COMMAND /delete in chat {message.chat.id}")
    try:
        bot.delete_message(message.chat.id, message.message_id)
        logger.info(f"Deleted command message {message.message_id}")
    except Exception as e:
        logger.error(f"Failed to delete message: {e}")

# ====== GROUP MESSAGE HANDLER ======
@bot.message_handler(func=lambda message: message.chat.type in ['group', 'supergroup'])
def handle_group_message(message):
    logger.info(f"=== GROUP MESSAGE DETECTED ===")
    logger.info(f"Group ID: {message.chat.id}")
    logger.info(f"Group Title: {message.chat.title}")
    logger.info(f"Group Type: {message.chat.type}")
    logger.info(f"User: {message.from_user.username} ({message.from_user.id})")
    logger.info(f"Message ID: {message.message_id}")
    logger.info(f"Text: {message.text}")
    logger.info(f"Has text: {bool(message.text)}")
    
    # Check bot permissions
    try:
        chat_member = bot.get_chat_member(message.chat.id, bot.get_me().id)
        logger.info(f"Bot status in group: {chat_member.status}")
        logger.info(f"Bot can delete messages: {getattr(chat_member, 'can_delete_messages', 'N/A')}")
        logger.info(f"Bot can restrict members: {getattr(chat_member, 'can_restrict_members', 'N/A')}")
    except Exception as e:
        logger.error(f"Error checking bot status: {e}")
    
    # Skip if it's a command
    if message.text and message.text.startswith('/'):
        logger.info(f"Ignoring command in group: {message.text}")
        return
    
    # Check for spam content
    if message.text and is_spam_message(message):
        logger.warning(f"SPAM FOUND! Attempting to delete message {message.message_id}")
        try:
            # Delete the spam message
            bot.delete_message(message.chat.id, message.message_id)
            logger.info(f"✅ SUCCESS: Deleted spam message {message.message_id} from {message.from_user.username}")
            
            # Send a warning
            warning_msg = bot.send_message(
                message.chat.id,
                f"⚠️ @{message.from_user.username or message.from_user.id} Please don't send spam!"
            )
            
            # Delete warning after 3 seconds
            time.sleep(3)
            bot.delete_message(message.chat.id, warning_msg.message_id)
            
        except Exception as e:
            logger.error(f"❌ FAILED to delete spam message: {e}")
            bot.send_message(message.chat.id, f"⚠️ Spam detected but I don't have permission to delete it!")
    
    # Rate limiting
    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()
    
    # Initialize tracking for this chat
    if chat_id not in user_message_count:
        user_message_count[chat_id] = {}
    
    if user_id not in user_message_count[chat_id]:
        user_message_count[chat_id][user_id] = {
            'count': 1,
            'first_time': current_time,
            'last_time': current_time
        }
    else:
        user_data = user_message_count[chat_id][user_id]
        user_data['count'] += 1
        
        # Check for flooding (8 messages in 15 seconds)
        if current_time - user_data['first_time'] <= 15 and user_data['count'] > 8:
            logger.warning(f"FLOOD DETECTED: User {user_id} sent {user_data['count']} messages in 15 seconds")
            try:
                bot.delete_message(chat_id, message.message_id)
                
                # Restrict user
                bot.restrict_chat_member(
                    chat_id=chat_id,
                    user_id=user_id,
                    until_date=int(time.time()) + 300,
                    can_send_messages=False,
                    can_send_media_messages=False,
                    can_send_other_messages=False,
                    can_add_web_page_previews=False
                )
                
                warning = bot.send_message(
                    chat_id,
                    f"🔇 User @{message.from_user.username or user_id} muted for 5 minutes for flooding."
                )
                time.sleep(5)
                bot.delete_message(chat_id, warning.message_id)
                
            except Exception as e:
                logger.error(f"Failed to mute user: {e}")
        elif current_time - user_data['first_time'] > 15:
            # Reset counter after 15 seconds
            user_data['count'] = 1
            user_data['first_time'] = current_time

# ====== PRIVATE MESSAGE HANDLER ======
@bot.message_handler(func=lambda message: message.chat.type == 'private')
def handle_private_message(message):
    logger.info(f"PRIVATE message from {message.from_user.username} ({message.chat.id}): {message.text}")
    
    # If it's not a command, just acknowledge
    if not message.text.startswith('/'):
        bot.reply_to(message, "I'm an anti-spam bot for groups! Add me to a group and make me admin.")

# ====== CATCH-ALL DEBUG HANDLER (LAST!) ======
@bot.message_handler(func=lambda message: True)
def debug_catch_all(message):
    logger.warning(f"=== UNHANDLED MESSAGE TYPE ===")
    logger.warning(f"Chat ID: {message.chat.id}")
    logger.warning(f"Chat Type: {message.chat.type}")
    logger.warning(f"Content Type: {message.content_type}")
    logger.warning(f"User: {message.from_user.username}")
    
    if message.content_type == 'text':
        logger.warning(f"Text: {message.text}")
    elif message.content_type == 'photo':
        logger.warning(f"Photo caption: {message.caption}")
    elif message.content_type == 'document':
        logger.warning(f"Document: {message.document.file_name}")

# Command to clear spam data
@bot.message_handler(commands=['clearspam'])
def clear_spam_data(message):
    logger.info(f"COMMAND /clearspam from {message.from_user.username}")
    try:
        user_status = bot.get_chat_member(message.chat.id, message.from_user.id).status
        if user_status in ['administrator', 'creator']:
            if message.chat.id in user_message_count:
                user_message_count[message.chat.id].clear()
            bot.reply_to(message, "✅ Spam detection data cleared!")
    except Exception as e:
        logger.error(f"Error in clearspam: {e}")

if __name__ == '__main__':
    bot_info = bot.get_me()
    logger.info(f"🤖 Bot starting: @{bot_info.username} (ID: {bot_info.id})")
    logger.info(f"Bot name: {bot_info.first_name}")
    
    print("=" * 50)
    print(f"🤖 Bot is ready: @{bot_info.username}")
    print("Add me to a group and use /checkperms to verify permissions")
    print("=" * 50)
    
    try:
        bot.infinity_polling(timeout=30, long_polling_timeout=5)
    except Exception as e:
        logger.error(f"Bot crashed: {e}")