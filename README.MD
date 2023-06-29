# Telegram Bot with ClickHouse Logging

This project implements a simple echo Telegram bot with logging capabilities using ClickHouse database. The bot also features user authentication and request throttling.

## Features

-   **Echo Messages:** The bot sends back any message it receives from an authorized user.
-   **User Authentication:** Only users that are whitelisted can interact with the bot.
-   **ClickHouse Logging:** All user interactions with the bot are logged in a ClickHouse database.
-   **Throttling:** Users are limited in the number of requests they can send to the bot within a certain time frame to prevent flooding.

## Getting Started

Clone the repository and navigate to the cloned directory:

bashCopy code

`git clone https://github.com/yourusername/telegram-bot-clickhouse-logging.git
cd telegram-bot-clickhouse-logging` 

## Prerequisites

-   Python 3.8+
-   aiohttp
-   aiogram
-   asynch
-   configparser
-   ClickHouse server

Install the Python requirements:

bashCopy code

`pip install -r requirements.txt` 

## Configuration

### Telegram Bot

Create a bot on Telegram and get your bot token. [How to create a bot](https://core.telegram.org/bots#creating-a-new-bot)

### ClickHouse

Set up a ClickHouse server. [ClickHouse Installation Instructions](https://clickhouse.tech/docs/en/getting-started/install/)

### settings.ini

In `config/settings.ini`:

-   Under `[TELEGRAM]`, set `BOT_TOKEN` to your Telegram bot token.
-   Under `[CLICKHOUSE]`, set:
    -   `HOST` to your ClickHouse server host.
    -   `PORT` to your ClickHouse server port.
    -   `DATABASE` to your ClickHouse database name.
    -   `USER` to your ClickHouse username.
    -   `PASSWORD` to your ClickHouse password.
    -   `TABLE` to your ClickHouse table name for logging.

### bot_lists.ini

In `config/bot_lists.ini`:

-   Under `[WHITELIST]`, set `LIST` to a comma-separated list of Telegram user IDs that are authorized to use the bot.

## Running the Bot

To start the bot:

bashCopy code

`python function/main_bot.py` 

## Files

The main files and directories in this project include:

-   `function/main_bot.py`: The main bot script.
-   `function/bot_helper.py`: Contains helper functions used by the bot.
-   `function/bot_middleware.py`: Contains middleware classes for ClickHouse logging, user authentication, and request throttling.
-   `bot_config.py`: Sets up the bot, dispatcher, and ClickHouse client.
-   `config/`: Directory containing configuration files.

## Author

Andrei Siniauski

## License

This project is licensed under the MIT License.

## Acknowledgments

-   [aiogram](https://github.com/aiogram/aiogram) for the Python framework for Telegram Bot API.
-   [aiohttp](https://github.com/aio-libs/aiohttp) for the HTTP client/server for asyncio.
-   [ClickHouse](https://clickhouse.tech/) for the open source column-oriented database management system that allows generating analytical data reports in real time.