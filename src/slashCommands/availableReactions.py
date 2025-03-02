import logging

from telebot import types
from src.core.rateLimiter import rateLimiterMessage
from src.core.setUp import Bot, validEmojis
logging.info(f"Added {__name__}")

@Bot.message_handler(commands=['reactions'])
@rateLimiterMessage
async def Start(message):
   text = "Here's all available reactions:\n" + " ".join(f"`{emoji}`" for emoji in validEmojis) + "\n\nClick To Copy"
   await Bot.reply_to(message,text,parse_mode="Markdown")