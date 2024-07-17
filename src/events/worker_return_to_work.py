try:
    from events.base import Event
except ModuleNotFoundError:
    from src.events.base import Event


class WorkerReturnToWork(Event):
    def __init__(self, time: float, worker, **kwargs):
        super().__init__(time, **kwargs)
        self.worker = worker

    @staticmethod
    def generate(time: float, worker_index: int, **kwargs):
        return WorkerReturnToWork(time + 1, worker_index)
