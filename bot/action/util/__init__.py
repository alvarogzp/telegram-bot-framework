def get_user_id_from_message(message):
    return message.from_.id if message.from_ is not None else "-"
