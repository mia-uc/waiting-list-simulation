class Event:
    def __init__(self, time: float, **kwargs):
        self.time = time

        for key, value in kwargs.items():
            setattr(self, key, value)

    def __lt__(self, other):
        return self.time < other.time

    def __gt__(self, other):
        return self.time > other.time

    def __eq__(self, other):
        return self.time == other.time

    def __str__(self):
        return f'{self.__class__.__name__}: {self.time}'
