import logging
import telebot
import emoji
import aiosqlite
from telebot import types
from src.core.rateLimiter import rateLimiterMessage
from src.core.setUp import Bot, validEmojis
from src.core.Database import checkUsersGroup, checkUserInfo
logging.info(f"Added {__name__}")

@Bot.message_handler(commands=['create','cr'])
@rateLimiterMessage
async def createReaction(message):
    """Handles the creation of automatic reactions for users in groups."""
    if message.chat.type not in ['group', 'supergroup']:
        return await Bot.reply_to(message, "This command is intended for groups only")
    
    usageMessage = "Usage\n```Non-Reply\n/create @Username {reaction}\n```\n```Reply\n/create {reaction}\n```"
    chatId = message.chat.id
    args = telebot.util.extract_arguments(message.text).split()
     
    # Check if the user is an admin
    chatAdmins = await Bot.get_chat_administrators(chatId)
    userIsAdmin = any(admin.user.id == message.from_user.id for admin in chatAdmins)

    if not userIsAdmin:
       return await Bot.reply_to(message, "You must be an admin to run this command", parse_mode="Markdown")
    
    # Determine username and reaction based on arguments and reply
    username, reaction = None, None
    if len(args) >= 2:
        username, reaction = args[0], args[1]
        if username.lower().endswith('bot'):
          return await Bot.reply_to(message, f"*You can't set auto reaction for a bot*\n{usageMessage}", parse_mode="Markdown")
    elif len(args) == 1 and message.reply_to_message:
      reaction = args[0]
      repliedUser = message.reply_to_message.from_user
      if not repliedUser or repliedUser.is_bot:
        return await Bot.reply_to(message, f"*You can't set auto reaction for a bot*\n{usageMessage}", parse_mode="Markdown")
      username = f"@{repliedUser.username}" if repliedUser.username else None

    # Validate inputs
    if not username or not username.startswith("@"):
        return await Bot.reply_to(message, f"*Enter a valid username*\n{usageMessage}", parse_mode="Markdown")
    
    if reaction not in validEmojis:
        return await Bot.reply_to(message, f"**Enter a valid emoji ( /reactions )**\n{usageMessage}", parse_mode="Markdown")

    # Check if the username already has a reaction
    addedUsernames = await checkUsersGroup(chatId)
    if username in addedUsernames:
       userData = await checkUserInfo(chatId, username)
       return await Bot.reply_to(message, f"{username} already has an auto reaction\nReaction: {userData[2]}", parse_mode="Markdown")

    # Save the reaction
    await saveReaction(chatId, username, reaction)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text=f"Edit {username}",callback_data=f"Edit:{username}:-1"))
    await Bot.reply_to(message, f"Reaction for {username} with {reaction} added successfully!\n\n" + "```\n/edit @Username {newReaction [leave blank for settings panel]}```",parse_mode="Markdown",reply_markup=markup)

async def saveReaction(chatId, username, reaction):
    """Saves the reaction configuration to the database."""
    query = """
    INSERT INTO `Groups` 
    (`chatId`, `Username`, `Reaction`, `mentionReaction`, `mentionReactionBig`, `replyReaction`, `replyReactionBig`) 
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    async with aiosqlite.connect('Database.db') as db:
        await db.execute(query, (chatId, username, reaction, 1, 0, 0, 0))
        await db.commit()
        await db.close()