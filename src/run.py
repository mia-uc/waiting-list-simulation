from simulation import Simulation

from entities.totem import Totem
from entities.workers import Seller, SellerAndClientSupport, ClientSupport

from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm

import pandas as pd


def run(index):
    s = Simulation(
        waiting_room_size=20,
        totem=Totem(),
        workers=[
            Seller(12),
            ClientSupport(12.5),
            Seller(13),
            ClientSupport(13.5)
        ]
    ).start().run()

    return [
        c.to_dict(simulation=index) for c in s.clients
    ]


if __name__ == '__main__':
    pool = ProcessPoolExecutor()
    n = 10000

    clients = []
    for cs in tqdm(pool.map(run, range(n)), total=n):
        clients.extend(cs)

    df = pd.DataFrame(clients)
    df.to_csv('clients.csv')
