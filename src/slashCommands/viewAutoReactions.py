import logging
from telebot import types
from src.core.setUp import Bot
from src.core.Database import checkGroupReactions
import src.slashCommands as slashCommands

logging.info(f"Added {__name__}")

userPages = {}
ITEMS_PER_PAGE = 1

async def sendPage(message, reactions, page, isEdit=False,userId=0):
    start = page * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    reactionsToShow = reactions[start:end]
    userId = message.from_user.id if not isEdit else userId

    if not reactionsToShow:
        text = "No reactions found."
    else:
        formattedReactions = "\n\n".join(
            [f"🧑‍💻 {user} {reaction}\n➡️ Mention : {'✅' if mentionReaction else '❌'} | Reply : {'✅' if replyReaction else '❌'}"
             for user, reaction, mentionReaction, replyReaction in reactionsToShow]
        )
        text = f"Auto Reactions for this group (Page {page + 1})\n{formattedReactions}"

    markup = types.InlineKeyboardMarkup(row_width=5)
    usersButtons = []
    for user, reaction, mentionReaction, replyReaction in reactionsToShow:
      usersButtons.append(types.InlineKeyboardButton(text=f"{user}",callback_data=f"Edit:{user}:{userId}:{page}"))
    markup.add(*usersButtons)
    # Create previous and next buttons
    buttons = []
    if page > 0:
        prevButton = types.InlineKeyboardButton("⬅️", callback_data=f"prev:{page - 1}:{userId}")
        buttons.append(prevButton)

    # Center the page number button, clickable to open a list of pages
    pageButton = types.InlineKeyboardButton(f"Page {page + 1}", callback_data=f"pages:{page}:{userId}")
    buttons.append(pageButton)

    if end < len(reactions):
        nextButton = types.InlineKeyboardButton("➡️", callback_data=f"next:{page + 1}:{userId}")
        buttons.append(nextButton)

    markup.add(*buttons)

    if isEdit:
        await Bot.edit_message_text(
            text,
            chat_id=message.chat.id,
            message_id=message.message_id,
            reply_markup=markup
        )
    else:
        await Bot.reply_to(message, text, reply_markup=markup)

# Generate a list of page buttons for the user to choose from
async def generatePageButtons(reactions, current_page,userId):
    total_pages = len(reactions) // ITEMS_PER_PAGE + (1 if len(reactions) % ITEMS_PER_PAGE > 0 else 0)
    page_buttons = []

    for i in range(total_pages):
        page_buttons.append(
            types.InlineKeyboardButton(f"Page {i + 1}", callback_data=f"jump:{i}:{userId}")
        )
    return page_buttons

@Bot.message_handler(commands=['view'])
async def view(message):
    if message.chat.type not in ['group', 'supergroup']:
        return await Bot.reply_to(message, "This command is intended for groups only")
    
    chatId = message.chat.id
    reactions = await checkGroupReactions(chatId)

    userPages[chatId] = 0
    await sendPage(message, reactions, userPages[chatId], isEdit=False)

@Bot.callback_query_handler(func=lambda call: call.data.startswith('next:') or call.data.startswith('prev:') or call.data.startswith('pages:') or call.data.startswith('jump:'))
async def handlePagination(call):
    # Extract the userId from the callback_data
    userId = call.data.split(':')[2]  # Assuming callback_data is like 'next:1:123456' or 'prev:0:123456'
    page = userPages.get(call.message.chat.id, 0)
    reactions = await checkGroupReactions(call.message.chat.id)

    # Check if the userId in the callback_data matches the user who clicked the button
    if int(userId) != call.from_user.id:
        return await Bot.answer_callback_query(call.id, "You cannot interact with this button", show_alert=True)

    if call.data.startswith("next:"):
        page += 1
    elif call.data.startswith("prev:"):
        page -= 1
    elif call.data.startswith("pages:"):
        page = int(call.data.split(':')[1])
    elif call.data.startswith("jump:"):
        page = int(call.data.split(':')[1])

    userPages[call.message.chat.id] = page

    if call.data.startswith("pages:"):  # Show the list of pages when user clicks on the page number
        page_buttons = await generatePageButtons(reactions, page,userId)
        markup = types.InlineKeyboardMarkup(row_width=5)
        markup.add(*page_buttons)
        text = f"Select a page (Current: {page + 1})"
        await Bot.edit_message_text(
            text,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=markup
        )
    else:
        await sendPage(call.message, reactions, page, isEdit=True,userId=userId)

@Bot.callback_query_handler(func=lambda call: call.data.startswith('Edit:'))
async def handleEdit(call):
   chatId = call.message.chat.id 
   username = call.data.split(':')[1]
   userId = call.data.split(':')[2]
   Page = call.data.split(':')[3]
   await slashCommands.sendReactionPanel(call.message,chatId,username,userId,IsEdit=True,backButton=True,Page=Page)