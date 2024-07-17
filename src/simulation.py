import time
import os
import argparse
import pandas as pd

from functools import singledispatchmethod

try:
    from random_vars import client as ClientRandomVar
    from utils.formatter import formatear_moneda

    from events.client_arrive import ClientArriveEvent
    from events.client_leave_totem import ClientLeaveTotemEvent
    from events.worker_return_to_work import WorkerReturnToWork
    from events.space_in_waiting_room import FeeSpaceInWaitingRoomEvent
    from events.client_leave import ClientLeave

    from entities.totem import Totem, TotemStatus
    from entities.client import ClientType, Client
    from entities.workers import Worker, WorkerStatus
    from entities.workers import Seller, SellerAndClientSupport, ClientSupport
except ModuleNotFoundError:
    from src.random_vars import client as ClientRandomVar
    from src.utils.formatter import formatear_moneda

    from src.events.client_arrive import ClientArriveEvent
    from src.events.client_leave_totem import ClientLeaveTotemEvent
    from src.events.worker_return_to_work import WorkerReturnToWork
    from src.events.space_in_waiting_room import FeeSpaceInWaitingRoomEvent
    from src.events.client_leave import ClientLeave

    from src.entities.totem import Totem, TotemStatus
    from src.entities.client import ClientType, Client
    from src.entities.workers import Worker, WorkerStatus
    from src.entities.workers import Seller, SellerAndClientSupport, ClientSupport


class Simulation:
    def __init__(
        self,
        waiting_room_size,
        totem: Totem,
        workers: list[Worker],
        start_hour=9,
        end_hour=18
    ):

        # Simulation Configuration
        self.clock = start_hour
        self.end_hour = end_hour
        self.waiting_room_size = waiting_room_size
        self.workers = workers
        self.totem = totem

        # Simulation Queues
        self.waiting_room: set[Client] = set()
        self.totem_waiting_list: list[Client] = []

        # Simulation Event Tools
        self.events = []

        # Simulation Memory
        self.clients = []

    #####################################################################
    # Simulation Test Rules
    ####################################################################

    def test_rules(self):
        assert len(self.waiting_room) <= self.waiting_room_size

        for client in self.totem_waiting_list:
            assert client.arrive_time is not None
            assert client.type is not None

        for client in self.waiting_room:
            assert client.waiting_room_arrive_time is not None
            assert client.ticker is not None
            assert client.requirement is not None

        clients = []
        for worker in self.workers:
            assert worker.queue[0] or \
                all(
                    worker.queue[i] is None
                    for i in range(1, len(worker.queue))
            )

            clients.extend(worker.queue)

        clients = [c for c in clients if c is not None]
        assert len(clients) == len(set(clients)), (clients, set(clients))

        totem_events = [
            e for e in self.events if isinstance(e, ClientLeaveTotemEvent)
        ]

        assert len(totem_events) <= 1

        worker_return_events = [
            e for e in self.events if isinstance(e, WorkerReturnToWork)
        ]

        assert len(worker_return_events) <= len(self.workers)

        client_leave_events = [
            e for e in self.events if isinstance(e, ClientLeave)
        ]

        assert len(client_leave_events) <= len(
            self.workers) - len(worker_return_events)

    #####################################################################
    # Simulation Main Methods
    ####################################################################

    def start(self):
        self.dispatch(ClientArriveEvent, ClientType.A)
        self.dispatch(ClientArriveEvent, ClientType.B)
        self.dispatch(ClientArriveEvent, ClientType.C)

        return self

    def run(self, delay=None, verbose=False, testing=False):
        while len(self.events) != 0:
            self.events.sort()
            event = self.events.pop(0)

            # The office door closes at the end hour, so, new client cannot arrive
            if self.end_hour < self.clock and isinstance(event, ClientArriveEvent):
                continue

            self.clock = event.time
            self.run_event(event)
            if verbose:
                output = f"Clock: {self.clock} --> {event}\n"
                output += f"Waiting Room ({len(self.waiting_room)}/{self.waiting_room_size}): {[str(client) for client in self.waiting_room]}\n"
                output += f"Totem Waiting Room ({len(self.totem_waiting_list)}): {'I'* len(self.totem_waiting_list)}\n"
                output += ''.join([
                    f"Monitor Worker({i}): {[str(client) if client else 'Empty' for client in worker.queue]}\n"
                    for i, worker in enumerate(self.workers)
                ])
                output += f"Events Queue: {[str(event) for event in self.events]}\n"
                output += "---------------------------------------------------------------------------------------------------------"

                print(output)
                # if delay is not None:
                #     time.sleep(delay)
                #     print("\033[F" * (10), end='')

                if delay is not None:
                    time.sleep(delay)
                    # clear_output(wait=True)
                    os.system('cls' if os.name == 'nt' else 'clear')

            # Run Passive Actions
            for worker in self.workers:
                self.passive_event(worker)

            self.passive_event(self.totem)

            if testing:
                self.test_rules()

        if verbose:
            print(output)

        return self

    #####################################################################
    # Event Handlers
    ####################################################################

    @singledispatchmethod
    def run_event(self):
        pass

    @run_event.register
    def _(self, event: ClientArriveEvent):
        # Add the new client to the totem waiting list
        self.totem_waiting_list.append(event.client)

        # Save the new client for computing final results
        self.clients.append(event.client)

        # Generate the new client arrive event with the same client arrive
        self.dispatch(ClientArriveEvent, event.client.type)

    @run_event.register
    def _(self, event: ClientLeaveTotemEvent):
        client = event.client

        # Update client's info
        client.waiting_room_arrive_time = self.clock
        client.ticker = self.totem.generate_ticker(client.type)

        # Add client to waiting room
        self.waiting_room.add(client)

        # If the waiting room is full the totem should be stopped
        if len(self.waiting_room) >= self.waiting_room_size:
            self.totem.stop()

    @run_event.register
    def _(self, event: ClientLeave):
        worker = event.worker
        event.client.leave_time = self.clock
        event.client.worker_helper = self.workers.index(worker)

        worker.free()

        if worker.go_to_launch(self.clock):
            self.dispatch(WorkerReturnToWork, worker)
            return

        if (next_client := worker.next()):
            self.dispatch(ClientLeave, next_client, worker=worker)

    @run_event.register
    def _(self, event: FeeSpaceInWaitingRoomEvent):
        if self.totem.status == TotemStatus.STOPPED:
            self.totem.start()

    @run_event.register
    def _(self, event: WorkerReturnToWork):
        event.worker.start()

        if (next_client := event.worker.next()):
            self.dispatch(ClientLeave, next_client, worker=event.worker)

    #####################################################################
    # Passive Actions
    ####################################################################

    @singledispatchmethod
    def passive_event(self):
        pass

    @passive_event.register
    def _(self, totem: Totem):
        if totem.status != TotemStatus.FREE:
            return

        # Before a new client moves to the totem
        # the totem waiting list must be cleaned to drop
        # each client who have left
        while self.totem_waiting_list and \
                ClientRandomVar.leakage_from_totem_waiting_list(
                    self.totem_waiting_list[0], self.clock
                ):

            client = self.totem_waiting_list.pop(0)
            client.price = ClientRandomVar.leakage_cost(client)
            client.leakage_time = self.clock

        # After the cleaning if there are clients in it yet
        # then the first moves to the totem
        if self.totem_waiting_list:
            client = self.totem_waiting_list.pop(0)
            self.totem.get_client(client)
            self.dispatch(ClientLeaveTotemEvent, client)

    @passive_event.register
    def _(self, worker: Worker):
        if worker.status == WorkerStatus.EATING:
            return

        if not self.waiting_room:
            return

        if worker.monitor_full():
            return

        clients = [c for c in self.waiting_room if worker.can_help(c)]
        clients.sort()

        free_new_space = False
        while clients:
            client = clients.pop(0)

            if not ClientRandomVar.leakage_from_waiting_room(client, self.clock):
                start_attention = worker.call(client)

                if start_attention:
                    # TODO: Add event to arrive a la fila del monitor
                    self.dispatch(ClientLeave, client, worker=worker)

            else:
                client.leakage_time = self.clock

            self.waiting_room.remove(client)
            free_new_space = True

            if worker.monitor_full():
                break

        if free_new_space:
            self.dispatch(FeeSpaceInWaitingRoomEvent)

    #####################################################################
    # Tools
    #####################################################################

    def get_worker(self, worker_index):
        try:
            return self.workers[worker_index]
        except IndexError:
            return self.workers[worker_index - len(self.workers)]

    def dispatch(self, new_event, *args, **kwargs):
        self.events.append(new_event.generate(self.clock, *args, **kwargs))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--delay", type=float, default=None)
    parser.add_argument("--q_len", type=int, default=2)

    args = parser.parse_args()

    s = Simulation(
        waiting_room_size=20,
        totem=Totem(),
        workers=[
            Seller(12, queue_len=args.q_len),
            ClientSupport(12.5, queue_len=args.q_len),
            Seller(13, queue_len=args.q_len),
            ClientSupport(13.5, queue_len=args.q_len)
        ]
    ).start().run(args.delay, verbose=True, testing=True)
