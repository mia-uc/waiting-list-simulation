from events.base import Event


class FeeSpaceInWaitingRoomEvent(Event):
    @staticmethod
    def generate(time: float, **kwargs):
        return FeeSpaceInWaitingRoomEvent(time)
