


class SerializeJson:
    def __init__(self):
        self.id = id(self)

    def to_json(self) -> dict:
        raise NotImplemented()

    def from_json(self, data, hashs=[]):
        raise NotImplemented()