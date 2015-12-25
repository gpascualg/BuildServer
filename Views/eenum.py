from enum import Enum

class EEnum(Enum):
    NONE = 0

    @classmethod
    def from_string(cls, data):
        try:
            return getattr(cls, data)
        except:
            return EEnum.NONE
