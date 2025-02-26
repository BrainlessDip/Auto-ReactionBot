import telebot
import logging
from src.core.setUp import Bot

logging.info(f"Added {__name__}")

class IsAdmin(telebot.custom_filters.SimpleCustomFilter):
   key='IsAdmin'
   @staticmethod
   def check(message: telebot.types.Message):
     return Bot.get_chat_member(message.chat.id,message.from_user.id).status in ['administrator','creator']
Bot.add_custom_filter(IsAdmin())

class IsGroup(telebot.custom_filters.SimpleCustomFilter):
   key='IsGroup'
   @staticmethod
   def check(message: telebot.types.Message):
     return message.chat.type in ['group','supergroup']
Bot.add_custom_filter(IsGroup())