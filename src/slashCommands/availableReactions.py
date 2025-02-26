import logging

from telebot import types
from src.core.setUp import Bot, validEmojis
logging.info(f"Added {__name__}")

@Bot.message_handler(commands=['reactions'])
async def Start(message):
   text = "Here's all available reactions:\n" + " ".join(validEmojis)
   await Bot.reply_to(message,text,parse_mode="Markdown")