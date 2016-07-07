from bot.action.core.action import Action


class SaveUserAction(Action):
    def post_setup(self):
        self.handler = UserStorageHandler(self.state)

    def process(self, event):
        message = event.message
        self.save_user(message.from_)
        self.save_user(message.forward_from)
        self.save_user(message.new_chat_member)
        self.save_user(message.left_chat_member)
        self.save_user(message.chat)

    def save_user(self, user):
        if user is not None:
            self.handler.save(user)


class UserStorageHandler:
    def __init__(self, state):
        self.state = state.get_for("user")

    def exists(self, user_id):
        return self.state.exists_value(str(user_id))

    def get(self, user_id):
        user = self.state.get_for(str(user_id))
        return {
            "id": user_id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
        }

    def save(self, user):
        user_store = self.state.get_for(str(user.id))
        if user.first_name != user_store.first_name:
            user_store.first_name = user.first_name
        if user.last_name != user_store.last_name:
            user_store.last_name = user.last_name
        if user.username != user_store.username:
            user_store.username = user.username
        if user.title != user_store.title:
            user_store.title = user.title
