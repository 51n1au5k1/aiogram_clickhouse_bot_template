# bot_config.py

import os
import asyncio
import configparser
from asynch import connect
from aiogram import Bot, Dispatcher
from bot_helper import Helper
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# Get the current directory and the path to the settings.ini configuration file
current_dir = os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(current_dir, 'config/settings.ini')

# Read the settings.ini configuration file
config = Helper.read_config(config_path)

# Extract the bot token from the configuration
TOKEN = config.get('TELEGRAM', 'BOT_TOKEN')

# Setup the ClickHouse configuration from the settings
clickhouse_config = {
    "host": config.get('CLICKHOUSE', 'HOST'),
    "port": config.getint('CLICKHOUSE', 'PORT'),
    "database": config.get('CLICKHOUSE', 'DATABASE'),
    "user": config.get('CLICKHOUSE', 'USER'),
    "password": config.get('CLICKHOUSE', 'PASSWORD'),
    "table": config.get('CLICKHOUSE', 'TABLE')
}

# Function to setup the ClickHouse client
def setup_clickhouse_client():
    # Asynchronous function to create the ClickHouse client
    async def create_clickhouse_client():
        conn = await connect(
            host=clickhouse_config['host'],
            port=clickhouse_config['port'],
            database=clickhouse_config['database'],
            user=clickhouse_config['user'],
            password=clickhouse_config['password'],
        )
        return conn

    # Run the asynchronous function until completion to create the ClickHouse client
    return asyncio.get_event_loop().run_until_complete(create_clickhouse_client())


# Create the bot instance using the token
bot = Bot(token=TOKEN)

# Create the ClickHouse client
clickhouse_client = setup_clickhouse_client()

# Create the Dispatcher instance using the bot instance and a memory storage
dp = Dispatcher(bot, storage=MemoryStorage())
