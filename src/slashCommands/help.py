import logging
from telebot.types import Message
from src.core.setUp import Bot

logging.info(f"Module {__name__} loaded successfully.")


@Bot.message_handler(commands=['help'])
async def display_help(message: Message):
    args = message.text.split()
    if len(args) == 1:
        help_text = """
*Auto Reaction Bot Help Menu*

Available commands:

- `/stats` : Displays bot statistics, including total users, groups, and reactions.

- `/create @Username {reaction}` : Sets an automatic reaction for a specified user.

- `/edit @Username {newReaction}` : Updates the automatic reaction for a specified user.

- `/reactions` : Lists all available reactions.

- `/view` : Shows the automatic reactions configured for the group.

For detailed information on a specific command, use `/help <command>`. Example: `/help create`
"""
    elif len(args) == 2:
        command = args[1].lower()
        if command in ['create', 'cr']:
            help_text = """
*Help for /create or /cr command*

Usage:
- Non-Reply: `/create @Username {reaction}`
- Reply: `/create {reaction}`

Requirements:
1. The command must be issued in a group or supergroup chat.
2. The username must start with `@`.
3. The reaction must be a valid emoji from the predefined list of `/reactions`.
4. The user must not already have an automatic reaction set.
"""
        elif command in ['edit', 'ed']:
            help_text = """
*Help for /edit or /ed command*

Usage:
- `/edit @Username` or `/ed @Username`
- Message Reply: `/edit` or `/ed`
- Alternatively: `/edit @Username {newReaction}` or `/ed @Username {newReaction}`

Requirements:
1. The command must be issued in a group or supergroup chat.
2. The username must start with `@`.
3. The reaction must be a valid emoji from the predefined list of `/reactions`.
"""
        elif command == 'stats':
            help_text = """
*Help for /stats command*

Usage:
- `/stats`: Displays bot statistics, including total users, groups, and reactions.
"""
        elif command == 'reactions':
            help_text = """
*Help for /reactions command*

Usage:
- `/reactions`: Lists all available reactions.
"""
        elif command == 'view':
            help_text = """
*Help for /view command*

Usage:
- `/view`: Shows the automatic reactions configured for the group.
"""
        else:
            help_text = "Invalid command. Use `/help` to see the list of available commands."
    else:
        help_text = "Invalid usage. Use `/help` to see the list of available commands."

    await Bot.reply_to(message, help_text, parse_mode="Markdown")
