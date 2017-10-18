# Telegram bot

This repository contains a Python framework to build bots against the [Telegram Bot API](https://core.telegram.org/bots), and an actually working bot.

The framework is action-based where you can configure what actions to perform when certain events occur (eg. someone enters a group, a command is sent to the bot, etc.).

You can find in [bot/manager.py](bot/manager.py) an already-configured bot using this framework.

A Python 3 interpreter is needed to run it.


## Set-up your own bot using this framework

1. Install `telegram-bot` with pip

       pip install https://github.com/alvarogzp/telegram-bot.git@master

   or add it as a dependency to your `requirements.txt`

       https://github.com/alvarogzp/telegram-bot.git@master#egg=telegram-bot

2. Create a `config/` dir in the base directory of your bot and add the following files inside it:

   - `auth_token`, and store there the auth token of the bot as provided by [@BotFather](https://t.me/BotFather).
   - `admin_user_id`, that must have the `user_id` of the admin of the bot (you can use [@userinfobot](https://t.me/userinfobot) to get yours). The admin can perform some sensitive tasks (like shutting down the bot).
   - `admin_chat_id`, with the `chat_id` of the chat you are going to use to manage the bot (you can set it to the same value as `admin_user_id` to use your private chat with the bot). This chat will be used to receive important messages from the bot. It is not recommended to disable notifications on this chat. If it is a group, the bot must be in it.
   - *Optional* `log_chat_id`, can be set to a `chat_id` where you would like the bot to send log messages. If not set, log messages will be discarded. If set to a group, the bot must be in it.
   - *Optional* `debug`, can have a value of `true` if you want requests and exception tracebacks to be printed on the standard output, and `false` if not. By default, they are enabled.
   - *Optional* `send_error_tracebacks`, can be `true` to send error tracebacks to `admin_chat_id` or `false` to not send them. By default they are sent.
   - *Optional* `async`, set it to `true` to enable asynchronous support on the bot, and to `false` to disable it. By default, it is enabled.
   - *Optional* `reuse_connections`, can be `true` to enable reusing of network connections to reduce response times by avoiding connection creation overhead, or `false` to disable it. By default it is enabled.
   - *Optional* `sleep_seconds_on_get_updates_error`, which indicates the seconds the bot sleeps when there is an error while getting updates, to avoid hitting the server repeatedly when it has problems. By default, the bot sleeps `60` seconds.

3. Copy the [main.py](main.py) and [bot/manager.py](bot/manager.py) files to your bot directory. Update `main.py` to use your new `BotManager` class instead of the framework one. Launch `main.py`. You now have a working bot with many features out-of-the-box! Configure them (to remove the ones you do not want, and add yours) in the `manager.py` file.

   - You can also copy [run.sh](run.sh) and use it as the launcher script for your bot. It performs some initialization tasks before running the bot, re-executes it if it crashes, and updates your VCS before running.

4. *Optional* To enable i18n support, copy the [locales](locales) dir to your bot base directory, and run its `generate_mo.sh` script (the `run.sh` script will do it for you if you are using it). Use the `locales/` dir as the base dir for your translations. You can use and modify the helper script `update_po.sh` to extract `.po` files from your code.
