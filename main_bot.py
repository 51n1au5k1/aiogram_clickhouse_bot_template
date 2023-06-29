# function/main_bot.py

import aiohttp
from aiogram import types
from aiogram.utils import executor
from bot_config import bot, dp, clickhouse_client
from bot_middleware import load_bot_lists, middleware_instances
from datetime import datetime

# Load bot lists
# These lists are used to check if a user is authorized to use the bot.
WHITELIST = load_bot_lists()
middleware_instances['auth'].whitelist = WHITELIST
middleware_instances['clickhouse'].whitelist = WHITELIST

# Message handler function
# This function is called every time a message is received by the bot.

@dp.message_handler()
async def echo_message(message: types.Message):
    # Authentication check
    # Preprocess the message with authentication middleware
    await middleware_instances['auth'].on_pre_process_message(message, {})

    # Send an echo reply back to the user
    await message.answer(message.text)

    # Log action in ClickHouse
    # Prepare user data and action details for logging
    user_id = str(message.from_user.id)
    first_name = message.from_user.first_name
    username = message.from_user.username
    last_name = message.from_user.last_name
    language_code = message.from_user.language_code
    action = message.text
    request = message.text
    response = message.text
    timestamp = datetime.now()

    # Log user action in ClickHouse
    await middleware_instances['clickhouse'].log_action(
        user_id,
        first_name,
        username,
        last_name,
        language_code,
        action,
        request,
        response,
        timestamp,
    )

# Main function to set up and run the bot
async def main():
    session = aiohttp.ClientSession()
    clickhouse_client = middleware_instances['clickhouse'].client
    auth_middleware = middleware_instances['auth']
    clickhouse_middleware = middleware_instances['clickhouse']
    dp.middleware.setup(clickhouse_middleware)
    dp.middleware.setup(auth_middleware)
    # Set up all other middleware
    for middleware in middleware_instances.values():
        if middleware not in [auth_middleware, clickhouse_middleware]:
            dp.middleware.setup(middleware)
    # Ensure that no existing webhook is running
    await bot.delete_webhook() 

    # Start polling for new messages
    try:
        await dp.start_polling()
    finally:
        # Close the session when done
        await session.close() 

# Entry point of the script
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)