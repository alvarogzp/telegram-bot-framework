import collections

import pytimeparse

from bot.action.core.action import Action
from bot.action.core.command import UnderscoredCommandBuilder
from bot.action.core.command.usagemessage import CommandUsageMessage
from bot.action.standard.userinfo import UserStorageHandler
from bot.action.util.counter import case_insensitive_counter
from bot.action.util.format import DateFormatter, UserFormatter
from bot.action.util.textformat import FormattedText
from bot.api.domain import Message, MessageEntityParser


class SaveHashtagsAction(Action):
    def process(self, event):
        hashtag_entities = self.get_hashtag_entities(event.message.entities)
        if len(hashtag_entities) > 0:
            new_hashtags = self.get_message_hashtags(event.message, hashtag_entities)
            if not new_hashtags.is_empty():
                HashtagStorageHandler(event).save_new_hashtags(new_hashtags)

    @staticmethod
    def get_hashtag_entities(entities):
        return [entity for entity in entities if entity.type == "hashtag"] if entities is not None else []

    def get_message_hashtags(self, message, hashtag_entities):
        entity_parser = MessageEntityParser(message)
        hashtags = HashtagList([])
        for entity in hashtag_entities:
            hashtag = self.get_hashtag_from_entity(message, entity, entity_parser)
            hashtags.add(hashtag)
        return hashtags

    @staticmethod
    def get_hashtag_from_entity(message, entity, entity_parser):
        hashtag = entity_parser.get_entity_text(entity)
        user_id = message.from_.id if message.from_ is not None else "-"
        return Hashtag(hashtag, message.date, user_id)


HASHTAGS_NO_FILTER_BY_TIME = -1


class ListHashtagsAction(Action):
    def process(self, event):
        action, action_param, help_args = self.parse_args(event.command_args.split())
        if action in ("recent", "popular", "ranking"):
            hashtags = HashtagStorageHandler(event).get_stored_hashtags()
            if hashtags.is_empty():
                response = self.get_response_empty()
            elif action == "recent":
                response = self.get_response_recent(event, hashtags, action_param)
            elif action == "popular":
                response = self.get_response_popular(event, hashtags, *action_param)
            else:
                response = self.get_response_ranking(event, hashtags, action_param)
        else:
            response = self.get_response_help(event, help_args)
        self.api.send_message(response.to_chat_replying(event.message))

    def parse_args(self, args):
        action = "help"
        action_param = 10
        help_args = args[1:]
        if len(args) == 0:
            action = "popular"
            action_param = (HASHTAGS_NO_FILTER_BY_TIME, 10, "")
        elif len(args) == 1:
            if args[0] not in ("popular", "recent", "ranking"):
                interval = self.parse_interval(args[0])
                if interval is not None:
                    action = "popular"
                    action_param = (interval, 10, args[0])
                elif args[0].isnumeric():
                    action = "popular"
                    action_param = (HASHTAGS_NO_FILTER_BY_TIME, int(args[0]), "")
            else:
                action = args[0]
        elif len(args) == 2:
            interval = self.parse_interval(args[0])
            if interval is not None and args[1].isnumeric():
                action = "popular"
                action_param = (interval, int(args[1]), args[0])
            elif args[0] == "popular":
                interval = self.parse_interval(args[1])
                if interval is not None:
                    action = "popular"
                    action_param = (interval, 10, args[1])
                elif args[1].isnumeric():
                    action = "popular"
                    action_param = (HASHTAGS_NO_FILTER_BY_TIME, int(args[1]), "")
            elif args[1].isnumeric():
                action_param = int(args[1])
                action = args[0]
        elif len(args) == 3:
            interval = self.parse_interval(args[1])
            if args[0] == "popular" and interval is not None and args[2].isnumeric():
                action = "popular"
                action_param = (interval, int(args[2]), args[1])
        return action, action_param, help_args

    @staticmethod
    def parse_interval(interval):
        if interval == "week":
            return 7 * 24 * 3600  # 7 days
        elif interval == "month":
            return 30 * 24 * 3600  # 30 days
        elif interval == "year":
            return 365 * 24 * 3600  # 365 days
        else:
            return pytimeparse.parse(interval)

    @staticmethod
    def get_response_help(event, help_args):
        args = ["[popular] [time_interval] [number_of_hashtags]", "recent [number_of_hashtags]", "ranking [number_of_users]"]
        description = "By default, display most popular hashtags.\n\n" \
                      "Use *recent* to show recent ones.\n\n" \
                      "Use *ranking* to show the users who wrote most hashtags.\n\n" \
                      "In any mode, you can also add a number to the end to limit the number of hashtags or users" \
                      " to display (default is 10).\n\n" \
                      "In the *popular* mode (the default one), you can add a time interval (eg. `week` or `10d`)" \
                      " to show most popular hashatgs between now and that interval.\n" \
                      "Currently, only day intervals are supported (ie. `30d`, `90d`, `1d`)."
        return CommandUsageMessage.get_usage_message(event.command, args, description)

    @staticmethod
    def get_response_empty():
        return Message.create("I have not seen any hashtag in this chat.\n"
                              "Write some and try again (hint: #ThisIsAHashTag).")

    def get_response_recent(self, event, hashtags, number_of_hashtags_to_display):
        user_storage_handler = UserStorageHandler.get_instance(self.state)
        sorted_hashtags = hashtags.sorted_by_recent_use(number_of_hashtags_to_display)
        printable_hashtags = sorted_hashtags.printable_version(user_storage_handler)
        ranking_hashtags_command = UnderscoredCommandBuilder.build_command(event.command, "ranking")
        ranking_hashtags_text = FormattedText().normal("Write ").normal(ranking_hashtags_command).normal(" to see which users write most hashtags.")
        return self.__build_success_response_message(event, "Most recent hashtags:", printable_hashtags, ranking_hashtags_text)

    def get_response_popular(self, event, hashtags, time_interval_in_seconds, number_of_hashtags_to_display, raw_interval):
        if time_interval_in_seconds != HASHTAGS_NO_FILTER_BY_TIME:
            oldest_requested_hashtag = event.message.date - time_interval_in_seconds
            hashtags = hashtags.filter_older_than(oldest_requested_hashtag)
            title = FormattedText().normal("Most popular hashtags during the last {interval}:").start_format().bold(interval=raw_interval).end_format()
        else:
            title = "Most popular hashtags:"
        printable_hashtags = hashtags.grouped_by_popularity(number_of_hashtags_to_display).printable_version()
        recent_hashtags_command = UnderscoredCommandBuilder.build_command(event.command, "recent")
        recent_hashtags_text = FormattedText().normal("Write ").normal(recent_hashtags_command).normal(" to see recent hashtags.")
        return self.__build_success_response_message(event, title, printable_hashtags, recent_hashtags_text)

    def get_response_ranking(self, event, hashtags, number_of_users_to_display):
        user_storage_handler = UserStorageHandler.get_instance(self.state)
        printable_hashtags = hashtags.grouped_by_user(number_of_users_to_display).printable_version(user_storage_handler)
        return self.__build_success_response_message(event, "Users who write most hashtags:", printable_hashtags)

    @staticmethod
    def __build_success_response_message(event, title, printable_hashtags, footer_text=None):
        if not isinstance(title, FormattedText):
            title = FormattedText().normal(title)
        footer = FormattedText().newline().newline()
        if footer_text is not None:
            footer.concat(footer_text)
        else:
            footer.normal("Write ").bold(event.command + " help").normal(" to see more options.")
        return FormattedText().concat(title).newline().normal(printable_hashtags).concat(footer).build_message()


class Hashtag:
    def __init__(self, hashtag, date=None, user_id=None):
        self.hashtag = hashtag
        self.date = int(date) if date is not None else -1
        self.user_id = user_id

    def printable_version(self, user_storage_handler):
        formatted_date = DateFormatter.format(self.date) if self.date != -1 else "???"
        formatted_user = UserFormatter.retrieve_and_format(self.user_id, user_storage_handler) if self.user_id is not None else "???"
        return "%s  (%s by %s)" % (self.hashtag, formatted_date, formatted_user)

    def serialize(self):
        return "%s %s %s\n" % (self.hashtag, self.date, self.user_id)

    @staticmethod
    def deserialize(hashtag_data):
        return Hashtag(*hashtag_data.split(" "))


class HashtagList:
    def __init__(self, hashtags):
        self.hashtags = hashtags

    def add(self, hashtag: Hashtag):
        self.hashtags.append(hashtag)

    def is_empty(self):
        return len(self.hashtags) == 0

    def grouped_by_popularity(self, max_to_return):
        hashtags_names = (hashtag.hashtag for hashtag in self.hashtags)
        return HashtagGroup(case_insensitive_counter(hashtags_names).most_common(max_to_return))

    def grouped_by_user(self, max_to_return):
        hashtags_users = (hashtag.user_id for hashtag in self.hashtags)
        return UserGroup(collections.Counter(hashtags_users).most_common(max_to_return))

    def sorted_by_recent_use(self, limit):
        if limit <= 0:
            return HashtagList([])
        # for now, assume they are already sorted by date
        return HashtagList(reversed(self.hashtags[-limit:]))

    def filter_older_than(self, timestamp):
        return HashtagList(filter(lambda hashtag: hashtag.date > timestamp, self.hashtags))

    def printable_version(self, user_storage_handler):
        return "\n".join((hashtag.printable_version(user_storage_handler) for hashtag in self.hashtags))

    def serialize(self):
        return "".join((hashtag.serialize() for hashtag in self.hashtags))

    @staticmethod
    def deserialize(hashtags_data):
        return HashtagList([Hashtag.deserialize(hashtag) for hashtag in hashtags_data.splitlines()])


class HashtagGroup:
    def __init__(self, grouped_hashtags):
        self.grouped_hashtags = grouped_hashtags

    def printable_version(self):
        return "\n".join(("%s → %s" % (count, hashtag) for hashtag, count in self.grouped_hashtags))


class UserGroup:
    def __init__(self, grouped_users):
        self.grouped_users = grouped_users

    def printable_version(self, user_storage_handler):
        return "\n".join(("%s → %s" % (count, UserFormatter.retrieve_and_format(user_id, user_storage_handler))
                          for user_id, count in self.grouped_users if user_id is not None))


class HashtagStorageHandler:
    def __init__(self, event):
        self.event = event

    def get_stored_hashtags(self):
        hashtags = self.event.state.hashtags
        if hashtags is None:
            hashtags = ""
        return HashtagList.deserialize(hashtags)

    def save_new_hashtags(self, hashtags: HashtagList):
        self.event.state.set_value("hashtags", hashtags.serialize(), append=True)
