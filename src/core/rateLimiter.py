import time
import logging
from collections import defaultdict
from functools import wraps
from telebot.types import Message, CallbackQuery
from src.core.setUp import Bot

logging.info(f"Added {__name__}")

# Dictionary to store user interaction timestamps
Interactions = defaultdict(list)

# Rate limit configuration
RATE_LIMIT = 1  # Maximum allowed interactions
TIME_WINDOW = 1  # Time window in seconds

# Rate limit decorator for callback queries
def rateLimiterCallback(callback):
    @wraps(callback)
    async def wrapper(call: CallbackQuery):
        userId = call.from_user.id
        currentTime = time.time()

        # Remove timestamps older than the time window
        Interactions[userId] = [
            t for t in Interactions[userId] if currentTime - t < TIME_WINDOW
        ]

        # Check if the user has exceeded the rate limit
        if len(Interactions[userId]) >= RATE_LIMIT:
            return await Bot.answer_callback_query(
                call.id, text="You're doing that too fast ☠️\nYou can't click more than once per second\nPlease wait a moment", show_alert=True)

        # Record the current interaction
        Interactions[userId].append(currentTime)

        # Call the original callback function
        return await callback(call)

    return wrapper

# Rate limit decorator for messages
def rateLimiterMessage(callback):
    @wraps(callback)
    async def wrapper(message: Message):
        userId = message.from_user.id
        currentTime = time.time()

        # Remove timestamps older than the time window
        Interactions[userId] = [
            t for t in Interactions[userId] if currentTime - t < TIME_WINDOW
        ]

        # Check if the user has exceeded the rate limit
        if len(Interactions[userId]) >= RATE_LIMIT:
            return await Bot.reply_to(message, "You're doing that too fast ☠️\nYou can't send message more than once per second\nPlease wait a moment")

        # Record the current interaction
        Interactions[userId].append(currentTime)

        # Call the original callback function
        return await callback(message)

    return wrapper