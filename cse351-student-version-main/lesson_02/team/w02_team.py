"""
Course: CSE 351 
Lesson: L02 team activity
File:   team.py
Author: <Add name here>

Purpose: Retrieve Star Wars details from a server

Instructions:

- This program requires that the server.py program be started in a terminal window.
- The program will retrieve the names of:
    - characters
    - planets
    - starships
    - vehicles
    - species

- the server will delay the request by 0.5 seconds

TODO
- Create a threaded class to make a call to the server where
  it retrieves data based on a URL.  The class should have a method
  called get_name() that returns the name of the character, planet, etc...
- The threaded class should only retrieve one URL.
  
- Speed up this program as fast as you can by:
    - creating as many as you can
    - start them all
    - join them all

"""

from datetime import datetime, timedelta
import threading

from common import *

# Include cse 351 common Python files
from cse351 import *

# global
call_count = 0
lock = threading.Lock()

class URLFetcher(threading.Thread):
    
    def __init__(self, url, kind_name):
        super().__init__()
        self.url = url
        self.kind_name = kind_name
        self.name_value = None
    
    def run(self):
        global call_count
        item = get_data_from_server(self.url)
        if item:
            self.name_value = item.get("name", "Unknown")
            with lock:
                call_count += 1
                print(f'  - {self.name_value}')
    
    def get_name(self):
        return self.name_value

def main():
    global call_count

    log = Log(show_terminal=True)
    log.start_timer('Starting to retrieve data from the server')

    film6 = get_data_from_server(f'{TOP_API_URL}/films/6')
    call_count += 1
    print_dict(film6)

    categories = ['characters', 'planets', 'starships', 'vehicles', 'species']
    
    for kind in categories:
        urls = film6[kind]
        print(kind)
        
        threads = []
        
        # Create thread for each URL
        for url in urls:
            thread = URLFetcher(url, kind)
            threads.append(thread)
            thread.start()
        
        # Join threads in category
        for thread in threads:
            thread.join()

    log.stop_timer('Total Time To complete')
    log.write(f'There were {call_count} calls to the server')

if __name__ == "__main__":
    main()
