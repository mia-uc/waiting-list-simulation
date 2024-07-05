from entities.client import ClientType
from collections import defaultdict


class TotemStatus:
    FREE = 'free'
    WORKING = 'working'
    STOPPED = 'stopped'


class Totem:
    def __init__(self) -> None:
        self.counter = defaultdict(int)
        self.status = TotemStatus.FREE

    def get_client(self, client):
        self.status = TotemStatus.WORKING

    def generate_ticker(self, client_type: ClientType):
        self.counter[client_type] += 1
        self.status = TotemStatus.FREE
        return self.counter[client_type]

    def stop(self):
        self.status = TotemStatus.STOPPED

    def start(self):
        self.status = TotemStatus.FREE
