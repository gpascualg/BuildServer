from enum import Enum
from switch import switch
import json

class WebhookType(Enum):
    NONE = 0
    PUSH = 1

    @staticmethod
    def from_data(data):
        try:
            return getattr(Enum, data.action)
        except:
            return NONE


class Webhook(object):
    def __init__(self, data):
        self.data = json.loads(data)

    def __getattribute__(self, arg):
        for case in switch(arg):

            if case('action'):
                return WebhookType.from_data(self.data)

            if case():
                return self.data[arg]

