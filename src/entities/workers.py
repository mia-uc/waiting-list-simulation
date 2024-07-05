class WorkerStatus:
    STOPPER = 'stopper'
    WORKING = 'working'
    EATING = "eating"


class Worker:

    def __init__(self, launch_time_start):
        self.status = WorkerStatus.STOPPER
        self.launch_time_start = launch_time_start
        self.have_launch = False

    def can_help(self, client):
        return True

    def go_to_launch(self, time):
        if not self.have_launch and time > self.launch_time_start:
            self.have_launch = True
            self.status = WorkerStatus.EATING
            return True

        return False

    def start(self):
        self.status = WorkerStatus.STOPPER


class SellerAndClientSupport(Worker):
    pass


class Seller(Worker):
    def can_help(self, client):
        return client.requirement == 1


class ClientSupport(Worker):
    def can_help(self, client):
        return client.requirement in [2, 3]
