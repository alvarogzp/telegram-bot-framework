from bot.action.standard.info.formatter import ApiObjectInfoFormatter
from bot.action.standard.info.formatter.chat import CHAT_TYPE_PRIVATE, CHAT_TYPE_CHANNEL
from bot.action.util.format import UserFormatter
from bot.api.api import Api
from bot.api.domain import ApiObject


MEMBER_STATUS_CREATOR = "creator"
MEMBER_STATUS_ADMINISTRATOR = "administrator"
MEMBER_STATUS_KICKED = "kicked"
MEMBER_STATUS_RESTRICTED = "restricted"


class UserInfoFormatter(ApiObjectInfoFormatter):
    def __init__(self, api: Api, user: ApiObject, chat: ApiObject):
        super().__init__(api, user)
        self.chat = chat

    def format(self, member_info: bool = False):
        """
        :param member_info: If True, adds also chat member info. Please, note that this additional info requires
            to make ONE api call.
        """
        user = self.api_object
        self.__format_user(user)
        if member_info and self.chat.type != CHAT_TYPE_PRIVATE:
            self._add_empty()
            self.__format_member(user)

    def __format_member(self, user: ApiObject):
        member = self.api.getChatMember(chat_id=self.chat.id, user_id=user.id)
        status = member.status
        self._add_title("Member info")
        self._add_info("Status", status)
        if status in (MEMBER_STATUS_RESTRICTED, MEMBER_STATUS_KICKED):
            until = self._date(member.until_date, "Forever")
            self._add_info("Until", until)
        if status == MEMBER_STATUS_ADMINISTRATOR:
            can_change_info = self._yes_no(member.can_change_info)
            can_delete_messages = self._yes_no(member.can_delete_messages)
            can_invite_users = self._yes_no(member.can_invite_users)
            can_restrict_members = self._yes_no(member.can_restrict_members)
            can_pin_messages = self._yes_no(member.can_pin_messages)
            can_promote_members = self._yes_no(member.can_promote_members)
            self._add_info("Can change chat info (title, photo, etc.)", can_change_info, separator="?")
            self._add_info("Can delete messages of other users", can_delete_messages, separator="?")
            self._add_info("Can invite new users", can_invite_users, separator="?")
            self._add_info("Can remove and restrict members", can_restrict_members, separator="?")
            self._add_info("Can pin messages", can_pin_messages, separator="?")
            self._add_info("Can add new admins", can_promote_members, separator="?")
            if self.chat.type == CHAT_TYPE_CHANNEL or \
                    member.can_post_messages is not None or member.can_edit_messages is not None:
                can_post_messages = self._yes_no(member.can_post_messages)
                can_edit_messages = self._yes_no(member.can_edit_messages)
                self._add_info("Can send messages (for channels only)", can_post_messages, separator="?")
                self._add_info("Can edit messages of other users (for channels only)", can_edit_messages, separator="?")
        if status == MEMBER_STATUS_RESTRICTED:
            can_send_messages = self._yes_no(member.can_send_messages)
            can_send_media_messages = self._yes_no(member.can_send_media_messages)
            can_send_other_messages = self._yes_no(member.can_send_other_messages)
            can_add_web_page_previews = self._yes_no(member.can_add_web_page_previews)
            self._add_info("Can send messages", can_send_messages, separator="?")
            self._add_info("Can send media messages (audio, photo & video)", can_send_media_messages, separator="?")
            self._add_info(
                "Can send other messages (stickers, gifs, games, inline bots)", can_send_other_messages, separator="?"
            )
            self._add_info("Can add web page previews", can_add_web_page_previews, separator="?")

    def __format_user(self, user: ApiObject):
        full_data = UserFormatter(user).full_data
        first_name = self._text(user.first_name)
        last_name = self._text(user.last_name)
        username = self._username(user.username)
        _id = user.id
        language_code = self._text(user.language_code)
        is_bot = self._yes_no(user.is_bot, yes_emoji="(🤖)", no_emoji="(👤)")
        self._add_title(full_data)
        self._add_empty()
        self._add_info("First name", first_name)
        self._add_info("Last name", last_name)
        self._add_info("Username", username)
        self._add_info("Id", _id)
        self._add_info("Language code", language_code)
        self._add_info("Is bot", is_bot, separator="?")
