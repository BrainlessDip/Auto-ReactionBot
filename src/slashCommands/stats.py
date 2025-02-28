import logging
import time 
import humanfriendly
from src.core.setUp import Bot
from src.core.rateLimiter import rateLimiterMessage
from src.core import allUsers, ReadDB, allGroups

logging.info(f"Added {__name__}")
startTime = int(time.time())
@Bot.message_handler(commands=['stats'])
@rateLimiterMessage
async def Stats(message):
   uptimeSeconds = int(time.time() - startTime)
   uptimeText = humanfriendly.format_timespan(uptimeSeconds)
   Text = f"Total Users: {len(await allUsers())}\nTotal Groups: {len(await allGroups())}\nTotal Reactions: {len(await ReadDB('Groups'))}\n\n```Uptime\n{uptimeText}\n```"
   await Bot.reply_to(message,Text,parse_mode="Markdown")