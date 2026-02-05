""" 
Course: CSE 351
Team  : Week 04
File  : team.py
Author: <Student Name>

See instructions in canvas for this team activity.

"""

import random
import threading

# Include CSE 351 common Python files. 
from cse351 import *

# Constants
MAX_QUEUE_SIZE = 10
PRIME_COUNT = 1000
FILENAME = 'primes.txt'
PRODUCERS = 3
CONSUMERS = 5

# ---------------------------------------------------------------------------
def is_prime(n: int):
    if n <= 3:
        return n > 1
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i ** 2 <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

# ---------------------------------------------------------------------------
class Queue351():
    """ This is the queue object to use for this class. Do not modify!! """

    def __init__(self):
        self.__items = []
   
    def put(self, item):
        assert len(self.__items) <= 10
        self.__items.append(item)

    def get(self):
        return self.__items.pop(0)

    def get_size(self):
        """ Return the size of the queue like queue.Queue does -> Approx size """
        extra = 1 if random.randint(1, 50) == 1 else 0
        if extra > 0:
            extra *= -1 if random.randint(1, 2) == 1 else 1
        return len(self.__items) + extra

# ---------------------------------------------------------------------------
def producer(id, que, empty_slots, full_slots, barrier):
    for i in range(PRIME_COUNT):
        number = random.randint(1, 1_000_000_000_000)
        
        # Acquire an empty slot before putting on queue
        empty_slots.acquire()
        que.put(number)
        # Release a full slot after putting on queue
        full_slots.release()

    # Wait for all producers to finish
    barrier.wait()

    # Select producer 0 to send "All Done" message
    if id == 0:
        for _ in range(CONSUMERS):
            empty_slots.acquire()
            que.put("All Done")
            full_slots.release()

# ---------------------------------------------------------------------------
def consumer(que, empty_slots, full_slots, filename, file_lock):
    while True:
        # Acquire a full slot before getting from queue
        full_slots.acquire()
        value = que.get()
        # Release an empty slot after getting from queue
        empty_slots.release()
        
        # Check if we received the "All Done" signal
        if value == "All Done":
            break
        
        # Check if the value is prime and write to file if it is
        if is_prime(value):
            with file_lock:
                with open(filename, 'a') as f:
                    f.write(f"{value}\n")

# ---------------------------------------------------------------------------
def main():

    random.seed(102030)

    # Clear the file at the start
    with open(FILENAME, 'w') as f:
        pass

    que = Queue351()

    # Create semaphores for the queue
    # empty_slots: tracks available empty slots in the queue (starts at MAX_QUEUE_SIZE)
    # full_slots: tracks available items in the queue (starts at 0)
    empty_slots = threading.Semaphore(MAX_QUEUE_SIZE)
    full_slots = threading.Semaphore(0)

    # Create a lock for file writing
    file_lock = threading.Lock()

    # Create barrier for all producers to synchronize
    barrier = threading.Barrier(PRODUCERS)

    # Create producers threads
    producers = []
    for i in range(PRODUCERS):
        p = threading.Thread(target=producer, args=(i, que, empty_slots, full_slots, barrier))
        p.start()
        producers.append(p)

    # Create consumers threads
    consumers = []
    for i in range(CONSUMERS):
        c = threading.Thread(target=consumer, args=(que, empty_slots, full_slots, FILENAME, file_lock))
        c.start()
        consumers.append(c)

    # Wait for all threads to complete
    for p in producers:
        p.join()
    
    for c in consumers:
        c.join()

    # Count and display results
    with open(FILENAME, 'r') as f:
        primes = len(f.readlines())
    print(f"Found {primes} primes. Must be 108 found.")



if __name__ == '__main__':
    main()
