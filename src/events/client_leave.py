try:
    from events.base import Event
    from entities.client import Client, ClientType
    from entities.workers import Worker
    from random_vars import client as ClientRandomVar
except ModuleNotFoundError:
    from src.events.base import Event
    from src.entities.client import Client, ClientType
    from src.entities.workers import Worker
    from src.random_vars import client as ClientRandomVar


class ClientLeave(Event):

    def __init__(self, time: float, client: Client, worker: Worker, **kwargs):
        super().__init__(time, **kwargs)
        self.client = client
        self.worker = worker

    @staticmethod
    def generate(time: float, client: Client, worker: Worker, **kwargs):
        worker.make_attention()

        delay = ClientRandomVar.get_attention(client.type, client.requirement)

        client.price = ClientRandomVar.get_price(
            client.type, client.requirement
        )
        client.attention_start_time = time

        return ClientLeave(time + delay, client, worker, **kwargs)
