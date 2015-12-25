from eenum import EEnum
from switch import switch
import json

class WebhookType(EEnum):
    PUSH = 1
    
    @classmethod
    def from_data(cls, data):
        return EEnum.from_string(data.action)


class Webhook(object):
    def __init__(self, data):
        self.data = json.loads(data)

    def __getattribute__(self, arg):
        for case in switch(arg):

            if case('action'):
                return WebhookType.from_data(self.data)

            if case():
                return self.data[arg]

