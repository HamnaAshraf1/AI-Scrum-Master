from abc import ABC

class slackuser(ABC):
    def __init__(self, user):
        self.user = user
        self.messages = dict()


    def conversation_grow(self, channel, role, message):
        if channel in self.messages.keys():
            self.messages[channel] += [{'role': role, 'content': message}]
        else:
            self.messages[channel] = [{'role': role, 'content': message}]


    def get_conversation(self, channel):
        if channel in self.messages.keys():
            return self.messages[channel]
        else:
            return []