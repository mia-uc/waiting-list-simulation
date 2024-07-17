try:
    from simulation import run, save
    from entities.totem import Totem
    from entities.workers import Seller, SellerAndClientSupport, ClientSupport
except ModuleNotFoundError:
    from src.simulation import Simulation
    from src.entities.totem import Totem
    from src.entities.workers import Seller, SellerAndClientSupport, ClientSupport

from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from tqdm import tqdm

import pandas as pd
import numpy as np
import os
import sys
from functools import partial

seed = 123456
np.random.seed(seed=seed)


def run(
    index,
    workers
):
    s = Simulation(
        waiting_room_size=20,
        totem=Totem(),
        workers=workers
    ).start().run()

    return [
        c.to_dict(simulation=index) for c in s.clients
    ]


def save(index, clients, path=''):
    df = pd.DataFrame(clients)
    df.to_csv(path + f's_{index}.csv')


options = {
    'clients_priority_req': [
        Seller(12),
        ClientSupport(12.5),
        Seller(13),
        ClientSupport(13.5),
    ],
    'clients': [
        Seller(12),
        ClientSupport(12.5),
        Seller(13),
        ClientSupport(13.5),
    ],
    'clients_plus_cs': [
        Seller(12),
        ClientSupport(12.5),
        Seller(13),
        ClientSupport(13.5),
        ClientSupport(14),
    ],
    'clients_plus_seller': [
        Seller(12),
        ClientSupport(12.5),
        Seller(13),
        ClientSupport(13.5),
        Seller(14),
    ],
    "clients_seller_and_cs": [
        SellerAndClientSupport(12),
        SellerAndClientSupport(12.5),
        SellerAndClientSupport(13),
        SellerAndClientSupport(13.5),
    ],
    'clients_q_1': [
        Seller(12, queue_len=1),
        ClientSupport(12.5, queue_len=1),
        Seller(13, queue_len=1),
        ClientSupport(13.5, queue_len=1),
    ],
    'clients_q_0': [
        Seller(12, queue_len=0),
        ClientSupport(12.5, queue_len=0),
        Seller(13, queue_len=0),
        ClientSupport(13.5, queue_len=0),
    ]
}

if __name__ == '__main__':

    if len(sys.argv) != 2:
        raise Exception(sys.argv)

    pool = ProcessPoolExecutor()
    thread = ThreadPoolExecutor()

    n = 372000

    client_type = sys.argv[-1]
    os.makedirs(client_type, exist_ok=True)
    f = partial(run, workers=options[client_type])

    for i, cs in tqdm(enumerate(pool.map(f, range(n))), total=n):
        thread.submit(save, f'{seed}-{i}', cs, f'./{client_type}/')

    pool.shutdown(True)
    thread.shutdown(True)
