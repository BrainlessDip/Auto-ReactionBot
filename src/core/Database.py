import aiosqlite

async def ReadFileData(Name):
   async with aiosqlite.connect('Database.db') as db:
     cursor = await db.cursor()
     await cursor.execute(f"SELECT * FROM {Name}")
     Users = await cursor.fetchall()
     await cursor.close()
     await db.close()
   return Users

async def ReadDB(Name):
   async with aiosqlite.connect('Database.db') as db:
     cursor = await db.cursor()
     await cursor.execute(f"SELECT * FROM {Name}")
     Users = [row[0] for row in await cursor.fetchall()]
     await cursor.close()
     await db.close()
   return Users

async def checkUsersGroup(chatId):
   async with aiosqlite.connect('Database.db') as db:
     cursor = await db.cursor()
     await cursor.execute(f"SELECT `Word` FROM 'Groups' WHERE `chatId` = {chatId}")
     Users = [row[0] for row in await cursor.fetchall()]
     await cursor.close()
     await db.close()
   return Users

async def checkGroupReactions(chatId):
    async with aiosqlite.connect('Database.db') as db:
      async with db.execute("SELECT `Word`, `Reaction`, `mentionReaction`, `replyReaction` FROM 'Groups' WHERE `chatId` = ?", (chatId,)) as cursor:
        Users = [(row[0], row[1], row[2], row[3]) for row in await cursor.fetchall()]
    await db.close()
    return Users

async def checkUserInfo(chatId, Word):
   async with aiosqlite.connect('Database.db') as db:
     cursor = await db.cursor()
     await cursor.execute("SELECT * FROM `Groups` WHERE `chatId` = ? AND `Word` = ?", (chatId, Word))
     User = await cursor.fetchall()
     User = User[0] if User else []
     await cursor.close()
     await db.close()
   return User

async def allUsers():
   async with aiosqlite.connect('Database.db') as db:
     cursor = await db.cursor()
     await cursor.execute("SELECT * FROM 'Users'")
     Users = [row[0] for row in await cursor.fetchall()]
     await cursor.close()
     await db.close()
   return Users

async def allGroups():
   async with aiosqlite.connect('Database.db') as db:
     cursor = await db.cursor()
     await cursor.execute("SELECT `chatId` FROM 'Groups'")
     Groups = list(set([row[0] for row in await cursor.fetchall()]))
     print(Groups)
     await cursor.close()
     await db.close()
   return Groups