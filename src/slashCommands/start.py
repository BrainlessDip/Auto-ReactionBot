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
Welcome to Auto Reaction Bot! 🤖

🌟 *Features:*
- *Mention Reaction:* Experience instant reactions when mentioning a triggered user
- *Reply Trigger:* Set a specific user for automatic reply reactions

🔧 *Customize:*
- Desire personalized reactions? Simply let me know!

Begin chatting and enjoy the cascade of reactions! 🚀
/help ? 
   """
   keyboard = types.InlineKeyboardMarkup()
   join_button = types.InlineKeyboardButton(text="Join Support Chat", url="https://t.me/AutoReactionSupport")
   keyboard.add(join_button)
   await Bot.reply_to(message,text,parse_mode="Markdown",reply_markup=keyboard)
   if message.chat.type == "private":
      await handleUser(message.chat.id, message)