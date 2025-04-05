import logging
from telebot import types
from src.core.setUp import Bot
from src.core.rateLimiter import rateLimiterCallback, rateLimiterMessage
from src.core.Database import checkGroupReactions
import src.slashCommands as slashCommands

logging.info(f"Added {__name__}")

userPages = {}
ITEMS_PER_PAGE = 3

async def sendPage(message, reactions, page, isEdit=False,userId=0):
    start = page * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    reactionsToShow = reactions[start:end]
    userId = message.from_user.id if not isEdit else userId

    if not reactionsToShow:
        text = "No reactions found"
    else:
        formattedReactions = "\n\n".join(
            [f"{'🧑‍💻' if word.startswith('@') else '🔠'} `{word}` • {reaction}\n➡️ Mention : {'✅' if mentionReaction else '❌'} | Reply : {'✅' if replyReaction else '❌'}"
             for word, reaction, mentionReaction, replyReaction in reactionsToShow])
        text = f"Auto Reactions for this group\nPage: {page + 1}\n\n{formattedReactions}"

    markup = types.InlineKeyboardMarkup(row_width=5)
    wordsButtons = []
    for word, reaction, mentionReaction, replyReaction in reactionsToShow:
      wordsButtons.append(types.InlineKeyboardButton(text=f"{word}",callback_data=f"Edit:{word}:{page}"))
    markup.add(*wordsButtons)
    # Create previous and next buttons
    buttons = []
    if page > 0:
        prevButton = types.InlineKeyboardButton("⬅️", callback_data=f"Prev:{page - 1}:{userId}")
        buttons.append(prevButton)

    # Center the page number button, clickable to open a list of pages
    if reactionsToShow:
      pageButton = types.InlineKeyboardButton(f"Page {page + 1}", callback_data=f"Pages:{page}:{userId}")
      buttons.append(pageButton)

    if end < len(reactions):
        nextButton = types.InlineKeyboardButton("➡️", callback_data=f"Next:{page + 1}:{userId}")
        buttons.append(nextButton)
    markup.add(*buttons)
    if isEdit:
        await Bot.edit_message_text(
            text,
            chat_id=message.chat.id,
            message_id=message.message_id,
            reply_markup=markup,
            parse_mode="Markdown"
        )
    else:
        await Bot.reply_to(message, text, reply_markup=markup,parse_mode="Markdown")

# Generate a list of page buttons for the user to choose from
async def generatePageButtons(reactions, current_page,userId):
    totalPages = len(reactions) // ITEMS_PER_PAGE + (1 if len(reactions) % ITEMS_PER_PAGE > 0 else 0)
    pageButtons = []

    for i in range(totalPages):
        pageButtons.append(
            types.InlineKeyboardButton(f"Page {i + 1}", callback_data=f"Jump:{i}:{userId}")
        )
    return pageButtons, totalPages

@Bot.message_handler(commands=['view'])
@rateLimiterMessage
async def view(message):
    if message.chat.type not in ['group', 'supergroup']:
        return await Bot.reply_to(message, "This command is intended for groups only")
    
    chatId = message.chat.id
    
    # Check if the user is an admin
    chatAdmins = await Bot.get_chat_administrators(chatId)
    userIsAdmin = any(admin.user.id == message.from_user.id for admin in chatAdmins)

    if not userIsAdmin:
       return await Bot.reply_to(message, "You must be an admin to run this command", parse_mode="Markdown")
    
    reactions = await checkGroupReactions(chatId)

    userPages[chatId] = 0
    await sendPage(message, reactions, userPages[chatId], isEdit=False)

@Bot.callback_query_handler(func=lambda call: call.data.startswith('Next:') or call.data.startswith('Prev:') or call.data.startswith('Pages:') or call.data.startswith('Jump:'))
@rateLimiterCallback
async def handlePagination(call):
    # Extract the userId from the callback_data
    userId = call.data.split(':')[2]  # Assuming callback_data is like 'Next:1:123456' or 'Prev:0:123456'
    page = userPages.get(call.message.chat.id, 0)
    reactions = await checkGroupReactions(call.message.chat.id)

    # Check if the userId in the callback_data matches the user who clicked the button
    if int(userId) != call.from_user.id:
        return await Bot.answer_callback_query(call.id, "You cannot interact with this button", show_alert=True)

    if call.data.startswith("Next:"):
        page += 1
    elif call.data.startswith("Prev:"):
        page -= 1
    elif call.data.startswith("Pages:"):
        page = int(call.data.split(':')[1])
    elif call.data.startswith("Jump:"):
        page = int(call.data.split(':')[1])
    userPages[call.message.chat.id] = page

    if call.data.startswith("Pages:"):  # Show the list of pages when user clicks on the page number
        pageButtons, totalPages = await generatePageButtons(reactions, page,userId)
        markup = types.InlineKeyboardMarkup(row_width=5)
        markup.add(*pageButtons, row_width=4)
        text = f"Select a page\nCurrent: {page + 1}\nTotal Page: {totalPages}"
        await Bot.edit_message_text(
            text,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=markup
        )
    else:
        if call.data.startswith("Jump:") and page < 0:
          page = len(reactions) // ITEMS_PER_PAGE + (1 if len(reactions) % ITEMS_PER_PAGE > 0 else 0)
          await sendPage(call.message, reactions, page-1, isEdit=True,userId=userId)
        else:
          await sendPage(call.message, reactions, page, isEdit=True,userId=userId)

@Bot.callback_query_handler(func=lambda call: call.data.startswith('Edit:'))
@rateLimiterCallback
async def handleEdit(call):
   chatId = call.message.chat.id 
   word = call.data.split(':')[1]
   
   if call.message.reply_to_message:
     userId = call.message.reply_to_message.from_user.id
   else:
     return await Bot.answer_callback_query(callback_query_id=call.id, text="Please verify that the reply to the message exists, or try running the command again", show_alert=True)
   
   Page = call.data.split(':')[2]
   if int(userId) != call.from_user.id:
     return await Bot.answer_callback_query(call.id, "You cannot interact with this button", show_alert=True)
   else:
     await slashCommands.sendReactionPanel(call.message,chatId,word,userId,IsEdit=True,Page=Page)