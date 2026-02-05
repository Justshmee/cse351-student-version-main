"""
Course    : CSE 351
Assignment: 04
Student   : Dylan

Instructions:
    - review instructions in the course

In order to retrieve a weather record from the server, Use the URL:

f'{TOP_API_URL}/record/{name}/{recno}

where:

name: name of the city
recno: record number starting from 0
"""

import time
import queue
from common import *
from cse351 import *

THREADS = 20
WORKERS = 10
RECORDS_TO_RETRIEVE = 5000  # Don't change


# ---------------------------------------------------------------------------
def retrieve_weather_data(cmd_q, data_q):
    while True:
        command = cmd_q.get()
        if command is None:
            cmd_q.task_done()
            break

        city, recno = command
        url = f'{TOP_API_URL}/record/{city}/{recno}'
        result = get_data_from_server(url)

        if result:
            data_q.put((result['city'], result['date'], result['temp']))

        cmd_q.task_done()


# ---------------------------------------------------------------------------
class Worker(threading.Thread):
    def __init__(self, data_q, noaa):
        super().__init__()
        self.data_q = data_q
        self.noaa = noaa

    def run(self):
        while True:
            item = self.data_q.get()
            if item is None:
                self.data_q.task_done()
                break

            city, date, temp = item
            self.noaa.add(city, temp)
            self.data_q.task_done()


# ---------------------------------------------------------------------------
class NOAA:
    def __init__(self):
        self.lock = threading.Lock()
        self.data = {city: [] for city in CITIES}

    def add(self, city, temp):
        with self.lock:
            self.data[city].append(temp)

    def get_temp_details(self, city):
        with self.lock:
            temps = self.data[city]
            return sum(temps) / len(temps) if temps else 0.0


# ---------------------------------------------------------------------------
def verify_noaa_results(noaa):

    answers = {
        'sandiego': 14.5004,
        'philadelphia': 14.865,
        'san_antonio': 14.638,
        'san_jose': 14.5756,
        'new_york': 14.6472,
        'houston': 14.591,
        'dallas': 14.835,
        'chicago': 14.6584,
        'los_angeles': 15.2346,
        'phoenix': 12.4404,
    }

    print()
    print('NOAA Results: Verifying Results')
    print('===================================')
    for name in CITIES:
        avg = noaa.get_temp_details(name)
        answer = answers[name]

        if abs(avg - answer) > 0.00001:
            msg = f'FAILED  Expected {answer}'
        else:
            msg = 'PASSED'

        print(f'{name:>15}: {avg:<10} {msg}')
    print('===================================')


# ---------------------------------------------------------------------------
def main():

    log = Log(show_terminal=True, filename_log='assignment.log')
    log.start_timer()

    noaa = NOAA()

    get_data_from_server(f'{TOP_API_URL}/start')

    print('Retrieving city details')
    print(f'{"City":>15}: Records')
    print('===================================')

    for city in CITIES:
        info = get_data_from_server(f'{TOP_API_URL}/city/{city}')
        print(f'{city:>15}: Records = {info["records"]:,}')

    print('===================================')

    cmd_q = queue.Queue(maxsize=10)
    data_q = queue.Queue(maxsize=10)

    # ✅ START WORKERS FIRST (prevents deadlock)
    workers = []
    for _ in range(WORKERS):
        w = Worker(data_q, noaa)
        w.start()
        workers.append(w)

    retrievers = []
    for _ in range(THREADS):
        t = threading.Thread(
            target=retrieve_weather_data,
            args=(cmd_q, data_q)
        )
        t.start()
        retrievers.append(t)

    for city in CITIES:
        for recno in range(RECORDS_TO_RETRIEVE):
            cmd_q.put((city, recno))

    for _ in retrievers:
        cmd_q.put(None)

    cmd_q.join()

    for _ in workers:
        data_q.put(None)

    data_q.join()

    data = get_data_from_server(f'{TOP_API_URL}/end')
    print(data)

    verify_noaa_results(noaa)
    log.stop_timer('Run time: ')


if __name__ == '__main__':
    main()
