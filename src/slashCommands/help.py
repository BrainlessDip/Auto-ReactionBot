
import logging
from telebot.types import Message
from src.core.rateLimiter import rateLimiterMessage
from src.core.setUp import Bot
import difflib  # Built-in library for string matching

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
- `/delete` : Delete the reaction for a user.

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
    "delete": """
*Help for /delete command*

Usage:
- `/delete`: Delete the reaction for a user
""",
    "error": "Invalid command. Use `/help` to see the list of available commands.",
    "invalid": "Invalid usage. Use `/help` to see the list of available commands"
}

logging.info(f"Added {len(HELP_TEXT)} Help Menu")

# Helper function to get available commands
def getAvailableCommands():
    return [key for key in HELP_TEXT.keys() if key not in {'invalid', 'default', 'error'}]

# Helper function to predict the closest command
def predictCommand(user_input, commands, cutoff=0.6):
    """
    Predicts the closest matching command using difflib.
    :param user_input: The user's input command.
    :param commands: List of available commands.
    :param cutoff: Minimum similarity score to consider a match (0 to 1).
    :return: The closest matching command or None if no match is found.
    """
    matches = difflib.get_close_matches(user_input, commands, n=1, cutoff=cutoff)
    return matches[0] if matches else None

@Bot.message_handler(commands=['help'])
@rateLimiterMessage
async def displayHelp(message: Message):
    args = message.text.split()
    
    if len(args) == 1:
        # Show default help menu
        Text = HELP_TEXT["default"]
    elif len(args) == 2:
        # Show help for a specific command
        user_input = args[1].lower()
        available_commands = getAvailableCommands()
        
        # Check if the user input matches a command exactly
        if user_input in available_commands:
            Text = HELP_TEXT[user_input]
        else:
            # Try to predict the closest command
            predictedCommand = predictCommand(user_input, available_commands)
            if predictedCommand:
                Text = f"\n\nDid you mean `/{predictedCommand}`?\n{HELP_TEXT[predictedCommand]}"
            else:
                Text = HELP_TEXT["error"]
        
        # Append available commands
        Text += f"\n\nAvailable Commands:\n{', '.join(available_commands)}"
    else:
        # Handle invalid usage
        Text = HELP_TEXT["invalid"]
        Text += f"\n\nAvailable Commands:\n{', '.join(getAvailableCommands())}"
    
    await Bot.reply_to(message, Text, parse_mode="Markdown")