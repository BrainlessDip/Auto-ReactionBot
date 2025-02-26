import logging
import telebot
import emoji
import aiosqlite
from src.core.setUp import Bot, validEmojis
from src.core.Database import checkUsersGroup, checkUserInfo
from telebot import types

logging.info(f"Added {__name__}")

@Bot.message_handler(commands=['edit','ed'])
async def editReaction(message):
    """Handles editing automatic reactions for users in groups."""
    if message.chat.type not in ['group', 'supergroup']:
        return await Bot.reply_to(message, "Group only")

    chatId = message.chat.id
    args = telebot.util.extract_arguments(message.text).split()
    usageMessage = "Usage\n```\n/edit @Username {newReaction [leave blank for settings panel]}\n```"

    # Check if the user is an admin
    chatAdmins = await Bot.get_chat_administrators(chatId)
    userIsAdmin = any(admin.user.id == message.from_user.id for admin in chatAdmins)

    if not userIsAdmin:
        return await Bot.reply_to(message, "You must be an admin to run this command.", parse_mode="Markdown")

    # Case 1: No arguments provided
    if len(args) == 0:
        username = None
        if message.reply_to_message:
            repliedUser = message.reply_to_message.from_user
            if not repliedUser or repliedUser.is_bot:
                return await Bot.reply_to(message, f"*You can't set auto reaction for a bot*\n{usageMessage}", parse_mode="Markdown")
            username = f"@{repliedUser.username}" if repliedUser.username else None
        if not username:
            return await Bot.reply_to(message, f"*Enter a valid username*\n{usageMessage}", parse_mode="Markdown")

        # Check if the username already has a reaction
        addedUsernames = await checkUsersGroup(chatId)
        if username not in addedUsernames:
            return await Bot.reply_to(message, f"{username} doesn't have an auto reaction set", parse_mode="Markdown")

        # Send the panel to change the reaction settings
        await sendReactionPanel(message,chatId, username, message.from_user.id)

    # Case 2: Two arguments provided (username and newReaction)
    elif len(args) == 2:
        username, newReaction = args[0], args[1]

        # Validate username
        if not username.startswith("@"):
            return await Bot.reply_to(message, f"*Enter a valid username*\n{usageMessage}", parse_mode="Markdown")

        # Check if the username already has a reaction
        addedUsernames = await checkUsersGroup(chatId)
        if username not in addedUsernames:
            return await Bot.reply_to(message, f"{username} doesn't have an auto reaction set", parse_mode="Markdown")

        # Validate new emoji
        if not emoji.is_emoji(newReaction) or newReaction not in validEmojis:
            return await Bot.reply_to(message, f"**Enter a valid emoji ( /reactions )**\n{usageMessage}", parse_mode="Markdown")

        # Update the reaction
        await updateReaction(chatId, username, newReaction)
        await Bot.reply_to(message, f"Reaction for {username} updated to {newReaction}!")

    # Case 3: One argument provided (only username)
    elif len(args) == 1:
        username = args[0]

        # Validate username
        if not username.startswith("@"):
            return await Bot.reply_to(message, f"*Enter a valid username*\n{usageMessage}", parse_mode="Markdown")

        # Check if the username already has a reaction
        addedUsernames = await checkUsersGroup(chatId)
        if username not in addedUsernames:
            return await Bot.reply_to(message, f"{username} doesn't have an auto reaction set", parse_mode="Markdown")

        # Send the panel to change the reaction settings
        await sendReactionPanel(message,chatId, username, message.from_user.id)

async def sendReactionPanel(message, chatId, username, userId, IsEdit=False,backButton=False,Page=1):
    """Send a panel with buttons to change the reaction settings."""
    markup = types.InlineKeyboardMarkup(row_width=2)

    # Fetch current settings for the user
    userData = await checkUserInfo(chatId, username)
    if not userData:
        return await Bot.reply_to(message, "No settings found for this user")

    # Define the settings map for user settings indices
    settingMap = {
        'mentionReaction': (3, "Mention Reaction"),
        'mentionReactionBig': (4, "Big Reaction(Mention)"),
        'replyReaction': (5, "Reply Reaction"),
        'replyReactionBig': (6, "Big Reaction(Reply)")
    }

    # Create two lists for the buttons
    mentionButtons = []
    replyButtons = []

    # Get the current setting values and display their statuses
    for settingName, (index, displayName) in settingMap.items():
        currentValue = userData[index]
        emoji = "✅" if currentValue else "❌"
        
        if settingName == "replyReactionBig" and not userData[5]:  # Only show if replyReaction is enabled
            continue
        if settingName == "mentionReactionBig" and not userData[3]:  # Only show if mentionReaction is enabled
            continue
        # Split into separate rows
        
        if "mention" in settingName:  # Mention-related reactions
            mentionButtons.append(types.InlineKeyboardButton(f"{emoji} {displayName}", callback_data=f"Toggle:{settingName}:{chatId}:{username}:{userId}"))
        elif "reply" in settingName:  # Reply-related reactions
            replyButtons.append(types.InlineKeyboardButton(f"{emoji} {displayName}", callback_data=f"Toggle:{settingName}:{chatId}:{username}:{userId}"))

    # Add Delete Button (separate row)
    deleteButton = types.InlineKeyboardButton("❌ Delete Reaction", callback_data=f"Delete:{chatId}:{username}:{userId}")

    # Add mention and reply buttons to the markup (in separate rows)
    if mentionButtons:
        markup.add(*mentionButtons)
    if replyButtons:
        markup.add(*replyButtons)
    markup.add(deleteButton)
    if backButton:
      markup.add(types.InlineKeyboardButton("Go Back", callback_data=f"jump:{Page}:{userId}"))

    # Send or edit the panel with the status message and buttons
    if IsEdit:
      await Bot.edit_message_text(message.text, chat_id=message.chat.id, message_id=message.message_id, reply_markup=markup, parse_mode="Markdown")
    else:
      await Bot.reply_to(message, f"Select an option to change settings for {username}", reply_markup=markup, parse_mode="Markdown")

@Bot.callback_query_handler(func=lambda call: call.data.startswith("Toggle:"))
async def handleToggle(call):
    """Handles the button clicks to Toggle the reaction settings."""
    _, settingName, chatId, username, userId = call.data.split(':')

    # Ensure that the user who clicked the button is the one who issued the command
    if int(userId) != call.from_user.id:
        return await Bot.answer_callback_query(call.id, "You cannot interact with this button", show_alert=True)

    # Fetch current settings for the user
    userData = await checkUserInfo(chatId, username)
    if not userData:
       return await Bot.answer_callback_query(call.id, f"{username} doesn't have an auto reaction set",show_alert=True)

    settingMap = {
        'mentionReaction': (3, "Mention Reaction"),
        'mentionReactionBig': (4, "Big Reaction - Mention"),
        'replyReaction': (5, "Reply Reaction"),
        'replyReactionBig': (6, "Big Reaction - Reply")
    }

    # Get the current setting value and Toggle it
    settingIndex = settingMap.get(settingName)[0]
    currentValue = userData[settingIndex]
    newValue = 0 if currentValue else 1

    # Update the setting in the database
    await updateUserSetting(chatId, username, settingName, newValue)
    
    settingName = settingMap.get(settingName)[1]
    # Update the callback query message
    await Bot.answer_callback_query(call.id, f"{settingName} for {username} {'Enabled ✅' if newValue else 'Disabled ❌'}")
    await sendReactionPanel(call.message,chatId, username, userId,IsEdit=True)

async def updateUserSetting(chatId, username, settingIndex, newValue):
    """Update a specific setting in the user's data."""
    query = f"""
    UPDATE `Groups`
    SET `{settingIndex}` = ?
    WHERE `chatId` = ? AND `Username` = ?
    """
    async with aiosqlite.connect('Database.db') as db:
        await db.execute(query, (newValue, chatId, username))
        await db.commit()
        await db.close()

async def updateReaction(chatId, username, newReaction):
    """Updates the reaction configuration in the database."""
    query = """
    UPDATE `Groups`
    SET `Reaction` = ?
    WHERE `chatId` = ? AND `Username` = ?
    """
    try:
        async with aiosqlite.connect('Database.db') as db:
            await db.execute(query, (newReaction, chatId, username))
            await db.commit()
            await db.close()
    except Exception as e:
        logging.error(f"Error updating reaction: {e}")
        raise
 
@Bot.callback_query_handler(func=lambda call: call.data.startswith("Delete:"))
async def deleteReactionSettings(call):
    """Handles the deletion of reaction settings for a user."""
    _, chatId, username, userId = call.data.split(':')

    # Ensure that the user who clicked the button is the one who issued the command
    if int(userId) != call.from_user.id:
        return await Bot.answer_callback_query(call.id, "You cannot interact with this button", show_alert=True)

    # Delete the reaction settings from the database
    try:
        await deleteUserSettings(chatId, username)
        await Bot.answer_callback_query(call.id, f"Reaction settings for {username} deleted ❌",show_alert=True)
        await Bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception as e:
        logging.error(f"Error deleting reaction settings: {e}")
        await Bot.answer_callback_query(call.id, "An error occurred while deleting reaction settings")

async def deleteUserSettings(chatId, username):
    """Deletes the user's settings from the database."""
    query = """
    DELETE FROM `Groups`
    WHERE `chatId` = ? AND `Username` = ?
    """
    try:
      async with aiosqlite.connect('Database.db') as db:
       cursor = await db.cursor()
       await cursor.execute(query, (chatId, username))
       await cursor.close()
       await db.commit()
       await db.close()
    except Exception as e:
        logging.error(f"Error deleting user settings: {e}")
        raise