# Telegram bot framework

This repository contains a Python framework to build bots against the [Telegram Bot API](https://core.telegram.org/bots), and a sample bot.

The framework is event-based where you can configure what actions to perform when certain events occur (eg. someone enters a group, a command is sent to the bot, etc.).

You can find in [bot/manager.py](bot/manager.py) an already-configured bot using this framework.

The framework works only on a Python 3 interpreter.
There are no plans to support Python 2, which will be [retired soon](https://pythonclock.org/).


## Set-up your own bot using this framework

1. Install `telegram-bot-framework` with pip

       pip install telegram-bot-framework

   or add `telegram-bot-framework` to `install_requires` in your `setup.py`, or to your `requirements.txt` file.

2. Create a `config/` dir in the base directory of your bot and add the configuration options specified in the [configuration section](#configuration) to it.

3. Copy the [main.py](main.py) and [bot/manager.py](bot/manager.py) files to your bot directory. Update `main.py` to use your new `BotManager` class instead of the framework one. Launch `main.py`. You now have a working bot with many features out-of-the-box! Configure them (to remove the ones you do not want, and add yours) in the `manager.py` file.

   - You can also copy [run.sh](run.sh) and use it as the launcher script for your bot. It performs some initialization tasks before running the bot, creates a virtual environment to install the dependencies and run the bot on it, re-executes the bot if it crashes, and updates your VCS before running.

4. *OPTIONAL* To enable i18n support, copy the [locales](locales) dir to your bot base directory, and run its `generate_mo.sh` script (the `run.sh` script will do it for you if you are using it). Use the `locales/` dir as the base dir for your translations. You can use and modify the helper script `update_po.sh` to extract `.po` files from your code.

You can use [XtremBot](https://github.com/alvarogzp/xtrem-bot) as an example of a simple bot using this framework.
Take a look at [World Times](https://github.com/alvarogzp/clock-bot) for a more elaborated bot.


## Configuration

The configuration is read from a `config/` dir in the working directory of the bot.

It consists of key-value entries where the key is the name of the file, and the value is the file content.

The following keys must be present for the bot to work properly (it will refuse to start if they are not set):

   - `auth_token`, with the auth token of the bot as provided by [@BotFather](https://t.me/BotFather).
   - `admin_user_id`, that must have the `user_id` of the admin of the bot (you can use [@userinfobot](https://t.me/userinfobot) to get yours). The admin can perform some sensitive tasks (like shutting down the bot).
   - `admin_chat_id`, with the `chat_id` of the chat you are going to use to manage the bot (you can set it to the same value as `admin_user_id` to use your private chat with the bot). This chat will be used to receive important messages from the bot. It is not recommended to disable notifications on this chat. If it is a group, the bot must be in it.

The following keys are also recognised by the framework, but they are *OPTIONAL*, and if not present, a default value is used:

   - `log_chat_id`, can be set to a `chat_id` where you would like the bot to send log messages. If not set, log messages will be discarded. If set to a group, the bot must be in it.
   - `debug`, can have a value of `true` if you want requests and exception tracebacks to be printed on the standard output, and `false` if not. By default, they are enabled.
   - `send_error_tracebacks`, can be `true` to send error tracebacks to `admin_chat_id` or `false` to not send them. By default they are sent.
   - `async`, set it to `true` to enable asynchronous support on the bot, and to `false` to disable it. By default, it is enabled.
   - `reuse_connections`, can be `true` to enable reusing of network connections to reduce response times by avoiding connection creation overhead, or `false` to disable it. By default it is enabled.
   - `scheduler_events_on_log_chat`, with a value of `true` to send scheduler event messages to log chat, and `false` to send them to admin chat. Note that initial scheduler events happening before logger is set-up are sent to admin chat regardless of this setting. By default, it is true.
   - `sleep_seconds_on_get_updates_error`, which indicates the number of seconds the bot sleeps when there is an error while getting updates, to avoid hitting the server repeatedly when it has problems. By default, the bot sleeps `60` seconds.
   - `max_error_seconds_allowed_in_normal_mode`, with the number of seconds the bot can be in normal mode while getting errors that avoid processing updates correctly. If this value is exceeded, the bot switches to process updates in pending mode, not answering to interactive actions (those under `NoPendingAction` in `BotManager`). The default is one hour.
   - `max_network_workers`, with the maximum number of workers (ie. threads) that can be running for network operations at the same time. By default, a maximum of 4 network workers are allowed.
   - `instance_name`, can be any string value to identify the bot instance at runtime.


## Known bots based on this framework

- [World Times](https://github.com/alvarogzp/clock-bot)
- [XtremBot](https://github.com/alvarogzp/xtrem-bot)


# Authors

- Developed by
  - Alvaro Gutierrez Perez
    - alvarogzp@gmail.com
    - https://linkedin.com/in/alvarogzp

- i18n support and visual improvements
  - [@KouteiCheke](https://github.com/KouteiCheke)
