processed_messages = set()


def is_processed(message_id):

    return message_id in processed_messages


def mark_processed(message_id):

    processed_messages.add(message_id)