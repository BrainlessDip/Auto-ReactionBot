import logging
import telebot
import aiosqlite
from src.core.rateLimiter import rateLimiterMessage
from src.core.setUp import Bot, validEmojis
from src.core.Database import checkUsersGroup, checkUserInfo

logging.info(f"Added {__name__}")


@Bot.message_handler(commands=['delete', 'del'])
@rateLimiterMessage
async def deleteReactionHandler(message):
    """Delete the reaction for a user"""

    # Ensure the command is used in a group or supergroup
    if message.chat.type not in ['group', 'supergroup']:
        return await Bot.reply_to(message, "This command is intended for groups only")

    chatId = message.chat.id
    args = telebot.util.extract_arguments(message.text).split()

    # Check if the user is an admin
    chatAdmins = await Bot.get_chat_administrators(chatId)
    if not any(admin.user.id == message.from_user.id for admin in chatAdmins):
        return await Bot.reply_to(message, "You must be an admin to run this command", parse_mode="Markdown")

    # Usage Message
    usageMessage = ("Usage\n```Non-Reply\n/delete @Username\n```\n"
                    "```Reply\n/delete\n```")

    # Determine word based on arguments or reply
    word = None
    if message.reply_to_message:
        # Extract word from the replied message
        repliedUser = message.reply_to_message.from_user
        if not repliedUser or repliedUser.is_bot:
            return await Bot.reply_to(message, f"*You can't delete a reaction for a bot*\n{usageMessage}", parse_mode="Markdown")
        word = f"@{repliedUser.username}" if repliedUser.username else None
    elif len(args) >= 1:
        # Extract word from the command arguments
        word = args[0]
    # check if the word is valid.
    if not word:
        return await Bot.reply_to(message, "No username was provided. Please provide a username or reply to user text.", parse_mode="Markdown")
    # Check if the username already has a reaction
    usersWithReactions = await checkUsersGroup(chatId)
    if word in usersWithReactions:
        await deleteReaction(chatId, word)
        await Bot.reply_to(message, f"Reaction for `{word}` deleted successfully!", parse_mode="Markdown")
    else:
        return await Bot.reply_to(message, f"`{word}` doesn't have any auto reaction", parse_mode="Markdown")


async def deleteReaction(chatId, word):
    """Deletes the reaction configuration from the database."""
    async with aiosqlite.connect('Database.db') as db:
        await db.execute("DELETE FROM `Groups` WHERE `chatId` = ? AND `Word` = ?", (chatId, word))
        await db.commit()
