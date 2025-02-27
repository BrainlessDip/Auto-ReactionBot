import logging
from telebot.types import Message
from src.core.setUp import Bot

logging.info(f"Added {__name__}")

# Define the help text in a dictionary for better maintainability
HELP_TEXT = {
    "default": """
*Auto Reaction Bot Help Menu*

Available commands:

- `/stats` : Displays bot statistics, including total users, groups, and reactions.
- `/create @Username {reaction}` : Sets an automatic reaction for a specified user.
- `/edit @Username {newReaction}` : Updates the automatic reaction for a specified user.
- `/reactions` : Lists all available reactions.
- `/view` : Shows the automatic reactions configured for the group.

For detailed information on a specific command, use `/help <command>`. Example: `/help create`
""",
    "create": """
*Help for /create or /cr command*

Usage:
- Non-Reply: `/create @Username {reaction}`
- Reply: `/create {reaction}`

Requirements:
1. The command must be issued in a group
2. The username must start with `@`
3. The reaction must be a valid emoji from the predefined list of /reactions
4. The user must not already have an automatic reaction set
""",
    "edit": """
*Help for /edit or /ed command*

Usage:
- `/edit @Username` or `/ed @Username`
- Message Reply: `/edit` or `/ed`
- Alternatively: `/edit @Username {newReaction}` or `/ed @Username {newReaction}`

Requirements:
1. The command must be issued in a group or supergroup chat.
2. The username must start with `@`.
3. The reaction must be a valid emoji from the predefined list of /reactions
""",
    "stats": """
*Help for /stats command*

Usage:
- `/stats`: Displays bot statistics, including total users, groups, and reactions.
""",
    "reactions": """
*Help for /reactions command*

Usage:
- `/reactions`: Lists all available reactions.
""",
    "view": """
*Help for /view command*

Usage:
- `/view`: Shows the automatic reactions configured for the group.
""",
    "error": "Invalid command. Use `/help` to see the list of available commands.",
    "invalid_usage": "Invalid usage. Use `/help` to see the list of available commands"
}
logging.info(f"Added {len(HELP_TEXT)} Help Menu")
@Bot.message_handler(commands=['help'])
async def displayHelp(message: Message):
    args = message.text.split()
    
    # Default to the general help text if no specific command is given
    if len(args) == 1:
        Text = HELP_TEXT["default"]
    elif len(args) == 2:
        command = args[1].lower()
        Text = HELP_TEXT.get(command, HELP_TEXT["error"])
    else:
        Text = HELP_TEXT["invalid_usage"]
    
    await Bot.reply_to(message, Text, parse_mode="Markdown")