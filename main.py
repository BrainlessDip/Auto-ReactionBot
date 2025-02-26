import asyncio
import logging
from src.core.setUp import Bot
import src.slashCommands, src.core

async def startBot():
   logging.info("BOT IS RUNNING")
   await Bot.polling(non_stop=True)

if __name__ == "__main__":
   asyncio.run(startBot()) 