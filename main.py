#!/usr/bin/env python3
from bot.actions.greet import GreetAction
from bot.actions.leave import LeaveAction
from bot.bot import Bot

if __name__ == "__main__":
    bot = Bot()
    bot.add_action(GreetAction())
    bot.add_action(LeaveAction())
    bot.run()
