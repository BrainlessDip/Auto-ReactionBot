# Auto ReactionBot

#### Project Status: <span style="color:#12b886">Active</span>

## Overview
This bot automatically reacts to messages in your Telegram group, allowing you to customize reactions for specific word (even user mention)
Contributions for new features are welcome!

## Usage Instructions
1. Add [@AutoReactionRoBot](https://t.me/AutoReactionRoBot) to your Telegram group.
2. The bot is now ready to use. Enjoy!

## Commands
The bot supports the following commands:

- **`/start`**: Displays a welcome message and provides a link to the support chat.
- **`/stats`**: Shows statistics about the bot, including total users, groups, and reactions.
- **`/create Word {reaction}`**: Sets an automatic reaction for a word
    - **Alias**: `cr`
    - **Usage**:
        - Non-Reply: `/create @Username {reaction}`
        - Reply: `/create {reaction}`
- **`/edit @Username {newReaction}`**: Updates the automatic reaction for a word.
    - **Alias**: `ed`
    - **Usage**:
        - `/edit @Username {newReaction}` (leave blank for settings panel)
- **`/reactions`**: Lists all available reactions.
- **`/view`**: Displays the automatic reactions set for the group.
- **`/help`**: Displays the help menu.
- **`/delete`**: Deletes the reaction for a word.
    - **Alias**: `del`

## Requirements for the `/create` Command
To use the `/create` command, ensure the following:
1. The command is issued in a group or supergroup chat.
2. The reaction is a valid emoji from the predefined list in `src/core/setUp.validEmojis`
3. The word does not already have an automatic reaction set

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

## Database Schema  
If `Database.db` does not exist or needs to be recreated, use the following command to import the schema:  

```sh
sqlite3 Database.db < db.schema
```  

For more details, check [this Stack Overflow post](https://stackoverflow.com/questions/18102976/how-to-create-a-db-file-in-sqlite3-using-a-schema-file).

## Reaction Priority  
It scans the message for matching words and reacts to the first one found  

If it's a reply and no matching words are found, it looks for a word directed at any username (words starting with `@`, reply reactions enabled)


## Support
- Public Support Group: [AutoReactionSupport](https://t.me/AutoReactionSupport)