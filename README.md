# Auto Reactor Bot (Telegram)

#### Project Status: <span style="color:#12b886">Active<span>

## Overview
This bot automatically reacts to messages in your Telegram group. Contributions for new features are welcome.

## Usage Instructions
1. Add `@AutoReactionRoBot` to your Telegram group.
2. The bot is now ready to use. Enjoy!

## Commands
The bot supports the following commands:

- `/start`: Displays a welcome message and provides a link to the support chat.
- `/stats`: Shows statistics about the bot, including total users, groups, and reactions.
- `/create @Username {reaction}`: Sets an automatic reaction for a user.
    - **Usage**:
        - Non-Reply: `/create @Username {reaction}`
        - Reply: `/create {reaction}`
- `/edit @Username {newReaction}`: Updates the automatic reaction for a user.
    - **Usage**:
        - `/edit @Username {newReaction [leave blank for settings panel]}`
- `/reactions`: Lists all available reactions.
- `/view`: Displays the automatic reactions set for the group.

## Requirements for the `/create` Command
To use the `/create` command, ensure the following:
1. The command is issued in a group or supergroup chat.
2. The username starts with `@`.
3. The reaction is a valid emoji from the predefined list of `validEmojis`.
4. The user does not already have an automatic reaction set.

## Hosting Instructions
1. Clone the repository:
     ```sh
     git clone https://github.com/BrainlessDip/Auto-ReactionBot.git
     ```
2. Navigate to the cloned directory and install Python dependencies:
     ```sh
     pip install -r requirements.txt
     ```
     Ensure Python is installed.
3. Create a `.env` file (a sample is provided in the source code).
4. Run the bot:
     ```sh
     python3 main.py
     ```

## Support
- Public Support Group: [AutoReactionSupport](https://t.me/AutoReactionSupport)
