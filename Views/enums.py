from enum import Enum

class EEnum(Enum):
    NONE = 0

    @classmethod
    def from_string(cls, data):
        try:
            return getattr(cls, data)
        except:
            return EEnum.NONE


class ServerRole(EEnum):
    ANNOUNCER = 1
    SLAVE = 2


class WebhookType(EEnum):
    PUSH = 1
    
    @classmethod
    def from_data(cls, data):
        return EEnum.from_string(data.action)

