import logging
from src.core.setUp import Bot
from src.core.Database import checkUsersGroup, checkUserInfo
from telebot import types

logging.info(f"Added {__name__}")

def isNotCommand(message):
    """Check if the message is not a command."""
    messageText = message.text if message.content_type == "text" else message.caption
    return not messageText or not messageText.startswith('/')

async def handleReaction(chatId, messageId, username, mode):
    """Handle setting message reactions based on user data."""
    userData = await checkUserInfo(chatId, username)
    if not userData:
        return

    # Extract reaction
    reaction = userData[2]

    # Map mode to corresponding indices
    modeIndices = {
        'mention': (3, 4),
        'reply': (5, 6)
    }

    # Extract status and isBig based on mode
    statusIndex, isBigIndex = modeIndices.get(mode, (None, None))
    if statusIndex is None or isBigIndex is None:
        return

    status = bool(userData[statusIndex])
    isBig = bool(userData[isBigIndex])

    # Set reaction if status is True
    if status:
      await Bot.set_message_reaction(chatId, messageId, [types.ReactionTypeEmoji(reaction)], is_big=isBig)

@Bot.message_handler(func=isNotCommand, content_types=['photo', 'video', 'document', 'text', 'sticker'])
async def processText(message):
    """Process messages to trigger reactions"""
    if message.chat.type in ['private','channel']:
        return

    # Extract message text or caption
    messageText = message.text if message.content_type == "text" else message.caption
    messageText = "None" if messageText is None else messageText

    chatId = message.chat.id
    reactionUsernames = await checkUsersGroup(chatId)

    # Check for direct mention in the message
    firstTriggered = next((username for username in messageText.split() if username in reactionUsernames), None)
    if firstTriggered:
       await handleReaction(chatId, message.message_id, firstTriggered,'mention')

    # Check for replies to users in reactionUsernames
    elif getattr(message.reply_to_message, 'from_user', None):
        username = f"@{message.reply_to_message.from_user.username}"
        if username in reactionUsernames:
           await handleReaction(chatId, message.message_id, username,'reply')