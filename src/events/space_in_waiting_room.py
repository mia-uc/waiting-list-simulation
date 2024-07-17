try:
    from events.base import Event
except ModuleNotFoundError:
    from src.events.base import Event


class FeeSpaceInWaitingRoomEvent(Event):
    @staticmethod
    def generate(time: float, **kwargs):
        return FeeSpaceInWaitingRoomEvent(time)
