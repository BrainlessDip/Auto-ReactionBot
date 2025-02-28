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

    # Determine username based on arguments or reply
    username = None
    if message.reply_to_message:
        # Extract username from the replied message
        repliedUser = message.reply_to_message.from_user
        if not repliedUser or repliedUser.is_bot:
            return await Bot.reply_to(message, f"*You can't delete a reaction for a bot*\n{usageMessage}", parse_mode="Markdown")
        username = f"@{repliedUser.username}" if repliedUser.username else None
    elif len(args) >= 1:
        # Extract username from the command arguments
        username = args[0]

    # Validate inputs
    if not username or not username.startswith("@"):
        return await Bot.reply_to(message, f"*Enter a valid username*\n{usageMessage}", parse_mode="Markdown")

    # Check if the username already has a reaction
    users_with_reactions = await checkUsersGroup(chatId)
    if username in users_with_reactions:
        await deleteReaction(chatId, username)
        await Bot.reply_to(message, f"Reaction for {username} deleted successfully!", parse_mode="Markdown")
    else:
        return await Bot.reply_to(message, f"{username} doesn't have any auto reaction", parse_mode="Markdown")

async def deleteReaction(chatId, username):
    """Deletes the reaction configuration from the database."""
    async with aiosqlite.connect('Database.db') as db:
        await db.execute("DELETE FROM `Groups` WHERE `chatId` = ? AND `Username` = ?", (chatId, username))
        await db.commit()