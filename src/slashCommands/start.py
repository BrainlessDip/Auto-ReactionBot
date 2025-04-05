import logging

from telebot import types
from src.core.setUp import Bot
from src.core.rateLimiter import rateLimiterMessage
from src.core import allUsers, handleUser

logging.info(f"Added {__name__}")

@Bot.message_handler(commands=['start'])
@rateLimiterMessage
async def Start(message):
   text = """
Welcome to the Auto Reaction Bot! 🤖

🌟 *Features:*
- *Mention Reactions:* Instantly trigger a reaction when a specific word or user is mentioned
- *Reply Triggers:* Instantly trigger a reaction when replying to a specific user

🔧 *Customization:*
- Personalize reaction for each word or user — pretty cool, right?

Start chatting and watch the reaction roll in! 🚀  
Type /help to learn how to use the bot
"""

   keyboard = types.InlineKeyboardMarkup()
   join_button = types.InlineKeyboardButton(text="Join Support Chat", url="https://t.me/AutoReactionSupport")
   keyboard.add(join_button)
   await Bot.reply_to(message,text,parse_mode="Markdown",reply_markup=keyboard)
   if message.chat.type == "private":
      await handleUser(message.chat.id, message)