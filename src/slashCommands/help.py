
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

- `/stats` : Displays bot statistics, including total words, groups, and reactions.
- `/create Word {reaction}` : Sets an automatic reaction for a specified word
- `/edit Word {newReaction}` : Updates the automatic reaction for a specified word.
- `/reactions` : Lists all available reactions.
- `/view` : Shows the automatic reactions configured for the group.
- `/delete` : Delete the reaction for a word

For detailed information on a specific command, use `/help <command>`. Example: `/help create`
""",
    "create": """
*Help for /create or /cr command*

Usage:
- Non-Reply: `/create Word {reaction}`
- Reply: `/create {reaction}`

Requirements:
1. The command must be issued in a group
3. The reaction must be a valid emoji from the predefined list of /reactions
4. The word must not already have an automatic reaction set
""",
    "edit": """
*Help for /edit or /ed command*

Usage:
- `/edit Word` or `/ed Word`
- Message Reply: `/edit` or `/ed`
- Alternatively: `/edit Word {newReaction}` or `/ed Word {newReaction}`

Requirements:
1. The command must be issued in a group or supergroup chat
3. The reaction must be a valid emoji from the predefined list of /reactions
""",
    "stats": """
*Help for /stats command*

Usage:
- `/stats`: Displays bot statistics, including total words, groups, and reactions.
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
- `/delete`: Delete the reaction for a word
""",
    "error": "Invalid command. Use `/help` to see the list of available commands.",
    "invalid": "Invalid usage. Use `/help` to see the list of available commands"
}

logging.info(f"Added {len(HELP_TEXT)} Help Menu")

# Helper function to get available commands
def getAvailableCommands():
    return [key for key in HELP_TEXT.keys() if key not in {'invalid', 'default', 'error'}]

# Helper function to predict the closest command
def predictCommand(word_input, commands, cutoff=0.6):
    """
    Predicts the closest matching command using difflib.
    :param word_input: The word's input command.
    :param commands: List of available commands.
    :param cutoff: Minimum similarity score to consider a match (0 to 1).
    :return: The closest matching command or None if no match is found.
    """
    matches = difflib.get_close_matches(word_input, commands, n=1, cutoff=cutoff)
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
        word_input = args[1].lower()
        available_commands = getAvailableCommands()
        
        # Check if the word input matches a command exactly
        if word_input in available_commands:
            Text = HELP_TEXT[word_input]
        else:
            # Try to predict the closest command
            predictedCommand = predictCommand(word_input, available_commands)
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