import aiosqlite
import logging

from src.core import allUsers

logging.info(f"Added {__name__}")

async def handleUser(userId, message):
     Users = await allUsers()
     if userId not in Users:
       await addUser(userId)
       logging.info(f"Add {message.from_user.username} ({userId})")

async def addUser(userId):
   async with aiosqlite.connect('Database.db') as db:
    cursor = await db.cursor()
    await cursor.execute(f"INSERT INTO `Users` (`userId`) VALUES ('{userId}');")
    await cursor.close()
    await db.commit()
    await db.close()