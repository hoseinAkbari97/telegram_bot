import os
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai

# ----------------------
# Load environment variables
# ----------------------
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN missing in .env file")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
else:
    print("Warning: GEMINI_API_KEY not found. Using echo mode for testing.")

# ----------------------
# Function to query Gemini
# ----------------------
def query_gemini(prompt: str) -> str:
    if not GEMINI_API_KEY:
        return f"Echo: {prompt} ( running in echo mode - add GEMINI_API_KEY to .env to use Gemini )"
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Gemini API error: {e}"

# ----------------------
# Telegram command handlers
# ----------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text(
            "سلام! 🤖\nمن یک ربات دموی چت هستم.\nهر چیزی می‌خوای بپرس!"
        )

async def ai_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_text = update.message.text
    await update.message.reply_text("⏳ در حال فکر کردن…")

    loop = asyncio.get_running_loop()
    answer = await loop.run_in_executor(None, query_gemini, user_text)
    await update.message.reply_text(answer)

# ----------------------
# Main function
# ----------------------
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_handler))

    print("Bot running… Press Ctrl+C to stop.")
    app.run_polling(close_loop=False)

if __name__ == "__main__":
    main()


# import os
# import logging
# from dotenv import load_dotenv
# from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
# from telegram.ext import (
#     Application,
#     CommandHandler,
#     MessageHandler,
#     CallbackQueryHandler,
#     ContextTypes,
#     filters,
# )
# from openai import OpenAI

# # --- logging setup ---
# logging.basicConfig(
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#     level=logging.INFO,
# )
# logger = logging.getLogger(__name__)

# # --- load env variables ---
# load_dotenv()
# BOT_TOKEN = os.getenv("BOT_TOKEN")
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# if not BOT_TOKEN or not OPENAI_API_KEY:
#     raise RuntimeError("BOT_TOKEN or OPENAI_API_KEY missing in .env file")

# # --- OpenAI client ---
# client = OpenAI(api_key=OPENAI_API_KEY)

# # --- command handlers ---
# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     if update.message:
#         keyboard = [[InlineKeyboardButton("Say hello", callback_data="hello")]]
#         reply_markup = InlineKeyboardMarkup(keyboard)
#         await update.message.reply_text(
#             "Hi! I'm your ChatGPT bot 🤖\nAsk me anything!",
#             reply_markup=reply_markup,
#         )

# async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     if update.message:
#         await update.message.reply_text("Just type a message, and I'll answer using ChatGPT!")

# # --- handle user messages (ChatGPT integration) ---
# async def chatgpt_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     if not update.message or not update.message.text:
#         return

#     user_text = update.message.text
#     await update.message.reply_text("⏳ Thinking...")

#     try:
#         response = client.chat.completions.create(
#             model="gpt-4o-mini",   # or "gpt-4.1-mini" / "gpt-4.1"
#             messages=[
#                 {"role": "system", "content": "You are a helpful assistant inside a Telegram bot."},
#                 {"role": "user", "content": user_text},
#             ],
#             max_tokens=500,
#         )
#         answer = response.choices[0].message.content.strip()
#         await update.message.reply_text(answer)

#     except Exception as e:
#         logger.error(f"OpenAI error: {e}")
#         await update.message.reply_text("⚠️ Sorry, something went wrong with ChatGPT.")

# # --- handle button presses ---
# async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     query = update.callback_query
#     await query.answer()
#     await query.edit_message_text("Hello from the button! ✨")

# # --- error handler ---
# async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
#     logger.exception("Exception while handling an update:", exc_info=context.error)

# def main():
#     app = Application.builder().token(BOT_TOKEN).build()

#     # register handlers
#     app.add_handler(CommandHandler("start", start))
#     app.add_handler(CommandHandler("help", help_cmd))
#     app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chatgpt_handler))
#     app.add_handler(CallbackQueryHandler(on_button))
#     app.add_error_handler(error_handler)

#     logger.info("Bot is starting… Press Ctrl+C to stop.")
#     app.run_polling(close_loop=False)

# if __name__ == "__main__":
#     main()
