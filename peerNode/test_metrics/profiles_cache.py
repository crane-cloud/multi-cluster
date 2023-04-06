import functools
import json
from collections import deque

#Function to retrieve data from the external data store

def retrieve_data():
    data = [
        {"timestamp": "2022-04-05T08:00:00", "cpu": 0.7, "memory": 0.9, "availability": 0.99}
    ]
    return data

# Initialize a deque to store the cached data
cached_data_queue = deque(maxlen=10)

# Define a function to cache the data retrieved from the external data store
@functools.lru_cache(maxsize=None)
def cached_data():
    print("Retriving new data points:")
    data = retrieve_data()
    cached_data_queue.append(json.dumps(data))
    return cached_data_queue[-1]

cached_data()

# Define a function to get the cached data as a list of dictionaries
def get_cached_data():
    if not cached_data_queue:
        return []
    return json.loads(cached_data_queue[-1])

print("Pick The latest data item in the queue:")
print(get_cached_data())