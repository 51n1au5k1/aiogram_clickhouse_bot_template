# function/bot_middleware.py

import os
import asyncio
from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.utils.exceptions import Throttled
from aiogram.dispatcher.handler import CancelHandler, current_handler
from aiogram.dispatcher import Dispatcher
from bot_config import clickhouse_config, clickhouse_client
from bot_helper import Helper
from aiogram.dispatcher import DEFAULT_RATE_LIMIT
from datetime import datetime

# Function to load the bot lists
def load_bot_lists():
    # Gets the current directory
    current_dir = os.path.dirname(os.path.realpath(__file__))
    # Defines the path to the bot lists
    bot_lists_config_path = os.path.join(current_dir, 'config/bot_lists.ini')
    # Reads the bot lists configuration file
    bot_lists_config = Helper.read_config(bot_lists_config_path)

    # Gets the whitelist from the configuration file
    WHITELIST = bot_lists_config.get('WHITELIST', 'LIST').split(',')

    return WHITELIST

# Middleware class for handling ClickHouse database actions
class ClickHouseMiddleware(BaseMiddleware):
    def __init__(self, clickhouse_client, whitelist):
        self.client = clickhouse_client
        self.whitelist = whitelist
        super().__init__()

    # Method executed before processing the message
    async def on_pre_process_message(self, message: types.Message, data: dict):
        if 'callback_query' in data:
            return

        # Extract user and message data
        user_id = str(message.from_user.id)
        first_name = message.from_user.first_name
        username = message.from_user.username
        last_name = message.from_user.last_name
        language_code = message.from_user.language_code
        action = message.text
        request = message.text
        response = None
        timestamp = datetime.now()

        # If the user is not in the whitelist
        if user_id not in self.whitelist:
            # Log unauthorized access
            await self.log_unauthorized_access(
                user_id, first_name, username, last_name, language_code, action, request, response, timestamp
            )
        else:
            # Log action
            await self.log_action(
                user_id, first_name, username, last_name, language_code, action, request, response, timestamp
            )

    # Method to log actions in ClickHouse
    async def log_action(
        self, user_id, first_name, username, last_name, language_code, action, request, response, timestamp
    ):
        formatted_timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        # SQL query for insertion
        query = f"INSERT INTO {clickhouse_config['table']} (user_id, first_name, username, last_name, language_code, " \
                f"action, request, response, timestamp) " \
                f"VALUES ('{user_id}', '{first_name}', '{username}', '{last_name}', '{language_code}', " \
                f"'{action}', '{request}', '{response}', '{formatted_timestamp}')"
        try:
            # Execute the query
            async with self.client.cursor() as cursor:
                await cursor.execute(query)
        except Exception as e:
            print(f"Error when trying to log action in ClickHouse: {e}")

    # Method to log unauthorized accesses in ClickHouse
    async def log_unauthorized_access(
        self, user_id, first_name, username, last_name, language_code, action, request, response, timestamp
    ):
        formatted_timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        # SQL query for insertion
        query = f"""
        INSERT INTO {clickhouse_config['table']} (user_id, first_name, username, last_name, language_code, action, request, response, timestamp)
        VALUES
        ('{user_id}', '{first_name}', '{username}', '{last_name}', '{language_code}', '{action}', '{request}', '{response}', '{formatted_timestamp}')
        """
        try:
            # Execute the query
            async with self.client.cursor() as cursor:
                await cursor.execute(query)
        except Exception as e:
            print(f"Error when trying to log unauthorized access in ClickHouse: {e}")

# Middleware class for handling authorization
class AuthMiddleware(BaseMiddleware):
    def __init__(self, whitelist, clickhouse_client):
        self.whitelist = whitelist
        self.clickhouse_client = clickhouse_client
        super().__init__()

    # Method executed before processing the message
    async def on_pre_process_message(self, message: types.Message, data: dict):
        user_id = str(message.from_user.id)
        first_name = message.from_user.first_name
        username = message.from_user.username
        last_name = message.from_user.last_name
        language_code = message.from_user.language_code
        action = message.text
        request = message.text
        response = 'Unauthorized access | Blocked'
        timestamp = datetime.now()

        if user_id not in self.whitelist:
            # If the user is not in the whitelist
            await message.reply("You are not authorized to use this bot.")
            
            # Log unauthorized access here before raising CancelHandler
            await middleware_instances['clickhouse'].log_unauthorized_access(
                user_id, first_name, username, last_name, language_code, action, request, response, timestamp
            )
            
            raise CancelHandler()

# Middleware class for handling throttling
class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, limit=DEFAULT_RATE_LIMIT, key_prefix='antiflood_'):
        self.rate_limit = limit
        self.prefix = key_prefix
        super(ThrottlingMiddleware, self).__init__()

    # Method executed before processing the message
    async def on_pre_process_message(self, message: types.Message, data: dict):
        handler = current_handler.get()
        dispatcher = Dispatcher.get_current()
        if handler:
            limit = getattr(handler, 'throttling_rate_limit', self.rate_limit)
            key = getattr(handler, 'throttling_key', f"{self.prefix}_{handler.__name__}")
        else:
            limit = self.rate_limit
            key = f"{self.prefix}_message"

        try:
            # Try to throttle the key
            await dispatcher.throttle(key, rate=limit)
        except Throttled as t:
            # Handle the Throttled exception
            await self.message_throttled(message, t)
            raise CancelHandler()

    # Method to log throttling access in ClickHouse
    async def log_throttling_access(self, user_id, first_name, username, last_name, language_code, action):
        formatted_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        response = "Throttling | Blocked"
        query = f"INSERT INTO {clickhouse_config['table']} (user_id, timestamp) VALUES ('{user_id}', '{formatted_timestamp}')"

        # Execute the query
        async with self.clickhouse_client.cursor() as cursor:
            await cursor.execute(query)

        # Log the throttling access in the ClickHouse table for user actions
        await middleware_instances['clickhouse'].log_action(
            user_id,
            first_name,
            username,
            last_name,
            language_code,
            action,
            None,
            response,
            datetime.now(),
        )

    # Method to handle the Throttled exception
    async def message_throttled(self, message: types.Message, throttled: Throttled):
        handler = current_handler.get()
        dispatcher = Dispatcher.get_current()
        if handler:
            key = getattr(handler, 'throttling_key', f"{self.prefix}_{handler.__name__}")
        else:
            key = f"{self.prefix}_message"

        delta = throttled.rate - throttled.delta

        if throttled.exceeded_count <= 2:
            await message.reply('Too many requests!')

        await asyncio.sleep(delta)

        thr = await dispatcher.check_key(key)

        if thr.exceeded_count == throttled.exceeded_count:
            await message.reply('Unlocked.')

            # Log throttling access if the message is still blocked
            await self.log_throttling_access(
                str(message.from_user.id),
                message.from_user.first_name,
                message.from_user.username,
                message.from_user.last_name,
                message.from_user.language_code,
                message.text,
            )

# Export middleware instances as a dictionary
middleware_instances = {
    'clickhouse': ClickHouseMiddleware(clickhouse_client, []),
    'auth': AuthMiddleware([], clickhouse_client),
    'throttling': ThrottlingMiddleware(),
}

# Load the whitelist
WHITELIST = load_bot_lists()
middleware_instances['clickhouse'].whitelist = WHITELIST
middleware_instances['auth'].whitelist = WHITELIST

# You can still use the individual instances if needed
clickhouse_middleware = middleware_instances['clickhouse']
auth_middleware = middleware_instances['auth']
throttling_middleware = middleware_instances['throttling']
