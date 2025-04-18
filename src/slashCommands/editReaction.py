import logging
import telebot
import emoji
import aiosqlite
from src.core.setUp import Bot, validEmojis
from src.core.rateLimiter import rateLimiterCallback, rateLimiterMessage
from src.core.Database import checkUsersGroup, checkUserInfo
from telebot import types

logging.info(f"Added {__name__}")

@Bot.message_handler(commands=['edit','ed'])
@rateLimiterMessage
async def editReaction(message):
    """Handles editing automatic reactions for users in groups."""
    if message.chat.type not in ['group', 'supergroup']:
        return await Bot.reply_to(message, "This command is intended for groups only")

    chatId = message.chat.id
    args = telebot.util.extract_arguments(message.text).split()
    usageMessage = "Usage\n```\n/edit Word {newReaction [leave blank for settings panel]}\n```"

    # Check if the user is an admin
    chatAdmins = await Bot.get_chat_administrators(chatId)
    userIsAdmin = any(admin.user.id == message.from_user.id for admin in chatAdmins)

    if not userIsAdmin:
        return await Bot.reply_to(message, "You must be an admin to run this command", parse_mode="Markdown")

    # Case 1: No arguments provided
    if len(args) == 0:
        word = None
        if message.reply_to_message:
            repliedUser = message.reply_to_message.from_user
            if not repliedUser or repliedUser.is_bot:
                return await Bot.reply_to(message, f"*You can't set auto reaction for a bot*\n{usageMessage}", parse_mode="Markdown")
            word = f"@{repliedUser.username}" if repliedUser.username else None
        if not word:
            return await Bot.reply_to(message, f"*Enter a valid word*\n{usageMessage}", parse_mode="Markdown")

        # Check if the word already has a reaction
        addedWords = await checkUsersGroup(chatId)
        if word not in addedWords:
            return await Bot.reply_to(message, f"{word} doesn't have an auto reaction set", parse_mode="Markdown")

        # Send the panel to change the reaction settings
        await sendReactionPanel(message,chatId, word, message.from_user.id)

    # Case 2: Two arguments provided (word and newReaction)
    elif len(args) == 2:
        word, newReaction = args[0], args[1]

        # Check if the word already has a reaction
        addedWords = await checkUsersGroup(chatId)
        if word not in addedWords:
            return await Bot.reply_to(message, f"{word} doesn't have an auto reaction set", parse_mode="Markdown")

        # Validate new emoji
        if not emoji.is_emoji(newReaction) or newReaction not in validEmojis:
            return await Bot.reply_to(message, f"**Enter a valid emoji ( /reactions )**\n{usageMessage}", parse_mode="Markdown")

        # Update the reaction
        await updateReaction(chatId, word, newReaction)
        await Bot.reply_to(message, f"Reaction for {word} updated to {newReaction}!")

    # Case 3: One argument provided (only word)
    elif len(args) == 1:
        word = args[0]

        # Check if the word already has a reaction
        addedWords = await checkUsersGroup(chatId)
        if word not in addedWords:
            return await Bot.reply_to(message, f"{word} doesn't have an auto reaction set", parse_mode="Markdown")

        # Send the panel to change the reaction settings
        await sendReactionPanel(message,chatId, word, message.from_user.id)

async def sendReactionPanel(message, chatId, word, userId, IsEdit=False,Page=0):
    """Send a panel with buttons to change the reaction settings."""
    markup = types.InlineKeyboardMarkup(row_width=2)

    # Fetch current settings for the user
    userData = await checkUserInfo(chatId, word)
    if not userData:
        return await Bot.reply_to(message, "No settings found for this user")

    userEmoji = userData[2]
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
            mentionButtons.append(types.InlineKeyboardButton(f"{emoji} {displayName}", callback_data=f"Toggle:{settingName}:{word}"))
        elif "reply" in settingName:  # Reply-related reactions
            replyButtons.append(types.InlineKeyboardButton(f"{emoji} {displayName}", callback_data=f"Toggle:{settingName}:{word}"))

    # Add Delete Button (separate row)
    deleteButton = types.InlineKeyboardButton("❌ Delete Reaction", callback_data=f"Delete:{word}:{userId}")
    deleteMsgButton = types.InlineKeyboardButton("❌ Delete Message", callback_data=f"DeleteMsg:{userId}")
    extraButtons = [deleteButton,deleteMsgButton]
    # Add mention and reply buttons to the markup (in separate rows)
    if mentionButtons:
       markup.add(*mentionButtons)
    if replyButtons and word.startswith('@'):
       markup.add(*replyButtons)
    markup.add(*extraButtons)
    markup.add(types.InlineKeyboardButton("Go Back", callback_data=f"Jump:{Page}:{userId}"))

    # Send or edit the panel with the status message and buttons
    messageText = f"Select an option to change settings for `{word}`\nReaction: {userEmoji}"
    if IsEdit:
      await Bot.edit_message_text(messageText, chat_id=message.chat.id, message_id=message.message_id, reply_markup=markup, parse_mode="Markdown")
    else:
      await Bot.reply_to(message, messageText, reply_markup=markup, parse_mode="Markdown")

@Bot.callback_query_handler(func=lambda call: call.data.startswith("Toggle:"))
@rateLimiterCallback
async def handleToggle(call):
    """Handles the button clicks to Toggle the reaction settings."""
    if call.message.reply_to_message:
      userId = call.message.reply_to_message.from_user.id
    else:
     return await Bot.answer_callback_query(callback_query_id=call.id, text="Please verify that the reply to the message exists, or try running the command again", show_alert=True)
    _, settingName, word = call.data.split(':')
    chatId = call.message.chat.id

    # Ensure that the user who clicked the button is the one who issued the command
    if int(userId) != call.from_user.id:
        return await Bot.answer_callback_query(call.id, "You cannot interact with this button", show_alert=True)

    # Fetch current settings for the user
    userData = await checkUserInfo(chatId, word)
    if not userData:
       return await Bot.answer_callback_query(call.id, f"{word} doesn't have an auto reaction set",show_alert=True)

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
    await updateUserSetting(chatId, word, settingName, newValue)
    
    settingName = settingMap.get(settingName)[1]
    # Update the callback query message
    await Bot.answer_callback_query(call.id, f"{settingName} for {word} {'Enabled ✅' if newValue else 'Disabled ❌'}")
    await sendReactionPanel(call.message,chatId, word, userId,IsEdit=True)

async def updateUserSetting(chatId, word, settingIndex, newValue):
    """Update a specific setting in the user's data."""
    query = f"""
    UPDATE `Groups`
    SET `{settingIndex}` = ?
    WHERE `chatId` = ? AND `Word` = ?
    """
    async with aiosqlite.connect('Database.db') as db:
        await db.execute(query, (newValue, chatId, word))
        await db.commit()
        await db.close()

async def updateReaction(chatId, word, newReaction):
    """Updates the reaction configuration in the database."""
    query = """
    UPDATE `Groups`
    SET `Reaction` = ?
    WHERE `chatId` = ? AND `Word` = ?
    """
    try:
        async with aiosqlite.connect('Database.db') as db:
            await db.execute(query, (newReaction, chatId, word))
            await db.commit()
            await db.close()
    except Exception as e:
        logging.error(f"Error updating reaction: {e}")
        raise
 
@Bot.callback_query_handler(func=lambda call: call.data.startswith("Delete:"))
@rateLimiterCallback
async def deleteReactionSettings(call):
    """Handles the deletion of reaction settings for a user."""
    _, word, userId = call.data.split(':')
    chatId = call.message.chat.id
    # Ensure that the user who clicked the button is the one who issued the command
    if int(userId) != call.from_user.id:
        return await Bot.answer_callback_query(call.id, "You cannot interact with this button", show_alert=True)

    # Delete the reaction settings from the database
    try:
        await deleteUserSettings(chatId, word)
        await Bot.answer_callback_query(call.id, f"Reaction settings for {word} deleted ❌",show_alert=True)
        Messages = []
        Messages.append(call.message.message_id)
        if call.message.reply_to_message:
          Messages.append(call.message.reply_to_message.message_id)
        try:
          return await Bot.delete_messages(call.message.chat.id , Messages)
        except Exception:
          return await Bot.delete_messages(call.message.chat.id, call.message.message_id)
    except Exception as e:
        logging.error(f"Error deleting reaction settings: {e}")
        await Bot.answer_callback_query(call.id, "An error occurred while deleting reaction settings")

async def deleteUserSettings(chatId, word):
    """Deletes the user's settings from the database."""
    query = """
    DELETE FROM `Groups`
    WHERE `chatId` = ? AND `Word` = ?
    """
    try:
      async with aiosqlite.connect('Database.db') as db:
       cursor = await db.cursor()
       await cursor.execute(query, (chatId, word))
       await cursor.close()
       await db.commit()
       await db.close()
    except Exception as e:
        logging.error(f"Error deleting user settings: {e}")
        raise

@Bot.callback_query_handler(func=lambda call: call.data.startswith("DeleteMsg:"))
@rateLimiterCallback
async def deleteMessage(call):
    """Handles the button clicks to Toggle the reaction settings."""
    _, userId = call.data.split(':')
    Messages = []
    Messages.append(call.message.message_id)
    if call.message.reply_to_message:
      Messages.append(call.message.reply_to_message.message_id)
    if int(userId) != call.from_user.id:
      return await Bot.answer_callback_query(call.id, "You cannot interact with this button", show_alert=True)
    else:
      try:
        return await Bot.delete_messages(call.message.chat.id , Messages)
      except Exception as e:
        return await Bot.answer_callback_query(call.id, str(e), show_alert=True)