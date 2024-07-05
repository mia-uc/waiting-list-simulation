import time
import os
import argparse

from functools import singledispatchmethod

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
        self.monitor_client_list = [None] * 2 * len(workers)

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

        for worker_index in range(len(self.workers)):
            assert self.monitor_client_list[worker_index] or \
                not self.monitor_client_list[worker_index + len(self.workers)]

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

    def run(self, delay=None, verbose=False):
        while len(self.events) != 0:
            self.events.sort()
            event = self.events.pop(0)

            # The office door closes at the end hour, so, new client cannot arrive
            if self.end_hour < self.clock and isinstance(event, ClientArriveEvent):
                continue

            self.clock = event.time
            self.run_event(event)
            if verbose:
                output = (
                    f"Clock: {self.clock} --> {event}\n"
                    f"Waiting Room ({len(self.waiting_room)}/{self.waiting_room_size}): {[str(client) for client in self.waiting_room]}\n"
                    f"Totem Waiting Room ({len(self.totem_waiting_list)}): {'I'* len(self.totem_waiting_list)}\n"
                    f"Monitor Client List: {[str(client) if client else 'Empty' for client in self.monitor_client_list]}\n"
                    f"Events Queue: {[str(event) for event in self.events]}\n"
                    "---------------------------------------------------------------------------------------------------------",
                )

                print(*output)
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

            self.test_rules()

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
        worker_index = event.worker_index
        event.client.leave_time = self.clock
        event.client.worker_helper = worker_index

        self.monitor_client_list[worker_index] = \
            self.monitor_client_list[worker_index + len(self.workers)]
        self.monitor_client_list[worker_index + len(self.workers)] = None

        if self.workers[worker_index].go_to_launch(self.clock):
            self.dispatch(WorkerReturnToWork, worker_index)
            return

        if self.monitor_client_list[worker_index] is not None:
            self.dispatch(
                ClientLeave,
                self.monitor_client_list[worker_index],
                worker_index=worker_index
            )

    @run_event.register
    def _(self, event: FeeSpaceInWaitingRoomEvent):
        if self.totem.status == TotemStatus.STOPPED:
            self.totem.start()

    @run_event.register
    def _(self, event: WorkerReturnToWork):
        self.workers[event.worker_index].start()

        if self.monitor_client_list[event.worker_index] is not None:
            self.dispatch(
                ClientLeave,
                self.monitor_client_list[event.worker_index],
                worker_index=event.worker_index
            )

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

        worker_index = self.workers.index(worker)

        if self.monitor_client_list[worker_index] and \
                self.monitor_client_list[worker_index + len(self.workers)]:
            return

        clients = [c for c in self.waiting_room if worker.can_help(c)]
        clients.sort()

        free_new_space = False
        while clients:
            client = clients.pop(0)

            if not ClientRandomVar.leakage_from_waiting_room(client, self.clock):

                if not self.monitor_client_list[worker_index]:
                    self.monitor_client_list[worker_index] = client
                    # TODO: Add event to arrive a la fila del monitor
                    self.dispatch(ClientLeave, client,
                                  worker_index=worker_index)

                elif not self.monitor_client_list[worker_index + len(self.workers)]:
                    self.monitor_client_list[worker_index +
                                             len(self.workers)] = client

                else:
                    break
            else:
                client.leakage_time = self.clock

            self.waiting_room.remove(client)
            free_new_space = True

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

    args = parser.parse_args()

    s = Simulation(
        waiting_room_size=20,
        totem=Totem(),
        workers=[
            Seller(12),
            ClientSupport(12.5),
            Seller(13),
            ClientSupport(13.5)
        ]
    ).start().run(args.delay, verbose=True)
