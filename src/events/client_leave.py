from events.base import Event
from entities.client import Client, ClientType
from random_vars import client as ClientRandomVar


class ClientLeave(Event):

    def __init__(self, time: float, client: Client, **kwargs):
        super().__init__(time, **kwargs)
        self.client = client

    @staticmethod
    def generate(time: float, client: Client, **kwargs):
        delay = ClientRandomVar.get_attention(client.type, client.requirement)
        client.price = ClientRandomVar.get_price(
            client.type, client.requirement
        )

        return ClientLeave(time + delay, client, **kwargs)
