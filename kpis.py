import os
import sys
import pandas as pd
import numpy as np
from scipy import stats
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
from functools import partial


def read_data(path):
    df = pd.read_csv(path)

    df['leakage'] = df['leave_time'].isna()

    df['attention_time'] = np.where(
        ~df['attention_start_time'].isna(),
        df['leave_time'] - df['attention_start_time'],
        df['attention_start_time']
    )

    df['system_time'] = np.where(
        ~df['leakage'],
        df['leave_time'] - df['arrive_time'],
        df['leakage_time'] - df['arrive_time']
    )

    df['waiting_time'] = np.where(
        ~df['waiting_room_arrive_time'].isna(),
        df['system_time'] + df['arrive_time'] - df["waiting_room_arrive_time"],
        df['waiting_room_arrive_time']
    )

    return df


def global_kpis(df):
    money = df['price'].sum()

    leakage_total = df['leakage'].sum() / len(df) * 100

    data = df[df['arrive_time'] < 12]
    leakage_total_morning = data['leakage'].sum() / len(data) * 100

    data = df[(df['arrive_time'] >= 12) & (df['arrive_time'] < 14)]
    leakage_total_noon = data['leakage'].sum() / len(data) * 100

    data = df[(df['arrive_time'] > 14)]
    leakage_total_evening = data['leakage'].sum() / len(data) * 100

    return {
        "total de clientes fugados": leakage_total,
        "total de clientes fugados en la mañana": leakage_total_morning,
        "total de clientes fugados al medio día": leakage_total_noon,
        "total de clientes fugados en la tarde": leakage_total_evening,
        "total de ingresos": money
    }


def clients_kpis(df, client_type):
    data = df[df['type'] == client_type]
    leakage_total = data['leakage'].sum() / len(data) * 100
    system_time = data['system_time'].sum() / len(data) * 100

    temp_data = data[~data['waiting_time'].isna()]
    waiting_time = temp_data['waiting_time'].sum() / len(temp_data) * 100

    return {
        f"total de clientes de tipo {client_type} fugados": leakage_total,
        f"Tiempo promedio en el sistema clientes tipo {client_type}": system_time,
        f"Tiempo promedio en la sala de espera clientes tipo {client_type}": waiting_time
    }


def worker_kpis(df, worker):
    data = df[(df['worker_helper'] == worker)]

    worker_time = data['attention_time'].sum() / (18-9-1) * 100
    worker_clients = len(data) / len(df) * 100

    return {
        f"Porcentaje de tiempo de trabajo el modulo {worker} empleado en la atención de clientes": worker_time,
        f"Porciento de clientes atendidos por el modulo {worker}": worker_clients
    }


def _aux(filename, directory):
    try:
        if filename.endswith('.csv'):
            file_path = os.path.join(directory, filename)
            df = read_data(file_path)

            return {
                **global_kpis(df),
                **clients_kpis(df, 'A'),
                **clients_kpis(df, 'B'),
                **clients_kpis(df, 'C'),
                **worker_kpis(df, 0.0),
                **worker_kpis(df, 1.0),
                **worker_kpis(df, 2.0),
                **worker_kpis(df, 3.0),
            }
    except:
        return None


def pandas_process_csv_files(directory):
    pool = ThreadPoolExecutor()

    dirs = os.listdir(directory)
    kpis = list(tqdm(
        pool.map(partial(_aux, directory=directory), dirs),
        total=len(dirs)
    ))

    kpis = [k for k in kpis if k]
    pool.shutdown(True)
    return pd.DataFrame(kpis)


if __name__ == '__main__':

    if len(sys.argv) != 2:
        raise Exception(sys.argv)

    client_type = sys.argv[-1]
    kpis = pandas_process_csv_files(f'./{client_type}')
    kpis.to_csv(f'./notebooks/{client_type}.csv')

    # kpis = pandas_process_csv_files('./clients_plus_cs')
    # kpis.to_csv('./notebooks/clients_plus_cs.csv')

    # kpis = pandas_process_csv_files('./clients_plus_seller')
    # kpis.to_csv('./notebooks/clients_plus_seller.csv')

    # kpis = pandas_process_csv_files('./clients_q_1')
    # kpis.to_csv('./notebooks/clients_q_1.csv')

    # kpis = pandas_process_csv_files('./clients_seller_and_cs')
    # kpis.to_csv('./notebooks/clients_seller_and_cs.csv')
