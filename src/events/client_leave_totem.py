from events.base import Event
from entities.client import Client, ClientType
from random_vars import client as ClientRandomVar


class ClientLeaveTotemEvent(Event):

    def __init__(self, time: float, client: Client, **kwargs):
        super().__init__(time, **kwargs)
        self.client = client

    @staticmethod
    def generate(time: float, client: Client, **kwargs):
        delay = ClientRandomVar.next_totem_finish(client.type)
        client.requirement = ClientRandomVar.select_requirement(client.type)
        return ClientLeaveTotemEvent(time + delay, client, **kwargs)
