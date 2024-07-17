from enum import Enum


class ClientType(Enum):
    A = 2
    B = 1
    C = 3


class Client:
    def __init__(self, type: ClientType, arrive_time: float) -> None:
        self.type = type
        self.arrive_time = arrive_time
        self.requirement = None
        self.waiting_room_arrive_time = None
        self.ticker = None
        self.attention_start_time = None
        self.price = None
        self.leave_time = None
        self.leakage_time = None
        self.worker_helper = None

    def to_dict(self, **kwargs):
        return {
            **kwargs,
            "type": self.type.name,
            "arrive_time": self.arrive_time,
            "requirement": self.requirement,
            "waiting_room_arrive_time": self.waiting_room_arrive_time,
            "ticker": self.ticker,
            "attention_start_time": self.attention_start_time,
            "price": self.price,
            "leave_time": self.leave_time,
            "leakage_time": self.leakage_time,
            "worker_helper": self.worker_helper
        }

    def __hash__(self) -> int:
        if self.ticker:
            return self.ticker

        return f"{self.type}-{self.arrive_time}"

    # def __lt__(self, other):
    #     if not other:
    #         return True

    #     if self.type == other.type:
    #         return self.arrive_time < other.arrive_time

    #     return self.type.value < other.type.value

    # def __gt__(self, other):
    #     if not other:
    #         return False

    #     if self.client_type == other.client_type:
    #         return self.arrive_time > other.arrive_time

    #     return self.client_type.value > other.client_type.value

    def __lt__(self, other):
        if not other:
            return True

        if self.requirement == 1 and other.requirement in [2, 3]:
            return True

        elif self.requirement == 3 and other.requirement == 2:
            return True

        elif self.requirement != 1 and other.requirement == 1:
            return False

        return self.arrive_time < other.arrive_time

    def __gt__(self, other):
        if not other:
            return False

        if self.requirement == 1 and other.requirement in [2, 3]:
            return False

        elif self.requirement == 3 and other.requirement == 2:
            return False

        elif self.requirement != 1 and other.requirement == 1:
            return True

        return self.arrive_time > other.arrive_time

    def __str__(self):
        if self.type == ClientType.A:
            return "A-" + str(self.ticker)

        if self.type == ClientType.B:
            return "B-" + str(self.ticker)

        if self.type == ClientType.C:
            return "C-" + str(self.ticker)
