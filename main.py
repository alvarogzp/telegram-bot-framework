#!/usr/bin/env python3

from bot.manager import BotManager

if __name__ == "__main__":
    bot_manager = BotManager()
    bot_manager.setup_actions()
    bot_manager.run()
