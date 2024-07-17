try:
    from events.base import Event
    from entities.client import Client, ClientType
    from random_vars import client as ClientRandomVar
except ModuleNotFoundError:
    from src.events.base import Event
    from src.entities.client import Client, ClientType
    from src.random_vars import client as ClientRandomVar


class ClientArriveEvent(Event):
    ClientClass = Client

    def __init__(self, time: float, client: Client, **kwargs):
        super().__init__(time, **kwargs)
        self.client = client

    @staticmethod
    def _is_morning(time):
        return 8 <= time < 12

    @staticmethod
    def _is_noon(time):
        return 12 <= time < 14

    @staticmethod
    def generate(time: float, client_type: ClientType, **kwargs):

        if ClientArriveEvent._is_morning(time):
            delay = ClientRandomVar.next_morning_arrive(client_type)

        elif ClientArriveEvent._is_noon(time):
            delay = ClientRandomVar.next_noon_arrive(client_type)

        else:
            delay = ClientRandomVar.next_evening_arrive(client_type)

        return ClientArriveEvent(
            time=time + delay,
            client=ClientArriveEvent.ClientClass(client_type, time + delay),
            **kwargs
        )
