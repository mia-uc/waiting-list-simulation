from events.base import Event


class WorkerReturnToWork(Event):
    def __init__(self, time: float, worker_index: int, **kwargs):
        super().__init__(time, **kwargs)
        self.worker_index = worker_index

    @staticmethod
    def generate(time: float, worker_index: int, **kwargs):
        return WorkerReturnToWork(time + 1, worker_index)
