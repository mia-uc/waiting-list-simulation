class WorkerStatus:
    STOPPER = 'stopper'
    WORKING = 'working'
    EATING = "eating"


class Worker:

    def __init__(self, launch_time_start, queue_len=2):
        self.status = WorkerStatus.STOPPER
        self.launch_time_start = launch_time_start
        self.have_launch = False

        self.queue = [None] * (queue_len + 1)

    def monitor_full(self):
        return all(x is not None for x in self.queue)

    @property
    def is_free(self):
        return self.status == WorkerStatus.STOPPER

    def free(self):
        self.status = WorkerStatus.STOPPER

    def next(self):
        assert self.status == WorkerStatus.STOPPER

        self.queue[0] = None

        if all(x is None for x in self.queue):
            return None

        while self.queue[0] is None:
            self.queue.pop(0)
            self.queue.append(None)

        return self.queue[0]

    def call(self, client):
        for index in range(len(self.queue)):
            if self.queue[index] is None:
                self.queue[index] = client
                break

        return index == 0 and self.is_free

    def can_help(self, client):
        return True

    def go_to_launch(self, time):
        assert self.status == WorkerStatus.STOPPER

        if not self.have_launch and time > self.launch_time_start:
            self.have_launch = True
            self.status = WorkerStatus.EATING
            return True

        return False

    def start(self):
        self.status = WorkerStatus.STOPPER

    def make_attention(self):
        self.status = WorkerStatus.WORKING


class SellerAndClientSupport(Worker):
    pass


class Seller(Worker):
    def can_help(self, client):
        return client.requirement == 1


class ClientSupport(Worker):
    def can_help(self, client):
        return client.requirement in [2, 3]
