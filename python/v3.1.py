import json
import random
from datetime import datetime, timedelta
import threading
import time

T0 = 1e6  # Initial temperature
ITER_COUNT = 1800000  # Iteration count
TRY_MAX = 1e6  # Maximum attempts
STAY_TIME = 300  # Default stay time in seconds
ALPHA = 0.9  # Cooling rate
EPSILON = 1e-3  # Minimum cost difference

# Global variable for progress tracking
progress = {}
progress_lock = threading.Lock()

class PostOffice:
    def __init__(self, num, name, info):
        self.num = num
        self.name = name
        self.info = info

class GMap:
    def __init__(self):
        self.pfs = {}

    def from_json(self, filename):
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for item in data['post_office']:
                post_office = PostOffice(item['index'], item['name'], item['info'])
                self.pfs[post_office.num] = post_office

def calculate_time_cost(route, pfs_v, now):
    total_cost = 0
    current_pfs = pfs_v[0]

    for i in range(len(route) - 1):
        from_pfs = route[i]
        to_pfs = route[i + 1]
        travel_time = current_pfs[from_pfs].info[str(to_pfs)][1]
        total_cost += travel_time
        now += timedelta(seconds=travel_time + STAY_TIME)

        # Update the time-based post office data
        if now.hour > 9 and now.hour <= 16:
            current_pfs = pfs_v[now.hour - 9]

    return total_cost

def sqa(start, pfs_v, iter_count, try_max, output_list, thread_id):
    global progress

    current_pfs = pfs_v[0]
    pf_vec = list(range(len(current_pfs)))
    pf_vec.remove(start)
    pf_vec = [start] + pf_vec + [start]
    now_vec = pf_vec.copy()
    shortest_vec = []
    shortest_time = float('inf')
    temperature = T0
    try_count = 0

    for iteration in range(iter_count):
        if try_count > try_max:
            output_list[thread_id] = f"Thread {thread_id}: Maximum attempts reached."
            break

        if temperature < EPSILON:
            output_list[thread_id] = f"Thread {thread_id}: Temperature too low, stopping."
            break

        now = datetime(2024, 9, 11, 9, 0, 0)
        current_cost = calculate_time_cost(now_vec, pfs_v, now)

        # Update progress
        with progress_lock:
            progress[thread_id] = f"Iteration {iteration}/{iter_count}" if iteration % 100 == 0 else progress[thread_id]

        # Evaluate the new route
        if current_cost < shortest_time:
            shortest_time = current_cost
            shortest_vec = now_vec.copy()
            temperature *= ALPHA
            try_count = 0

            output_list[thread_id] = f"Thread {thread_id}: Iteration {iteration}, New shortest time {shortest_time}"
        else:
            diff = current_cost - shortest_time
            acceptance_prob = 1 / (1 + pow(2.71828, diff / temperature))
            if random.random() < acceptance_prob:
                shortest_time = current_cost
                shortest_vec = now_vec.copy()

            try_count += 1

        # Randomly shuffle the route for next iteration
        first = random.randint(1, len(now_vec) - 2)
        second = random.randint(1, len(now_vec) - 2)
        while first == second:
            second = random.randint(1, len(now_vec) - 2)
        now_vec[first], now_vec[second] = now_vec[second], now_vec[first]

    output_list[thread_id] = f"Thread {thread_id}: Finished. Shortest Time: {shortest_time}, Path: {shortest_vec}"
    with progress_lock:
        progress[thread_id] = "Completed"

def display_progress(num_threads):
    global progress
    while True:
        with progress_lock:
            for thread_id in range(num_threads):
                status = progress.get(thread_id, "Not started")
                print(f"Thread {thread_id}: {status}", end=' | ')
            print("\r", end="")
        time.sleep(0.5)
        if all(progress.get(thread_id) == "Completed" for thread_id in range(num_threads)):
            break

def main():
    gm = GMap()
    now = None

    print("Welcome to the Postal Route Optimization Program")
    s = input("Enter start time (ex. 12:03:04 or -1 for now): ")

    if s == "-1":
        now = datetime.now()
    else:
        now = get_time(s)

    while now.hour < 9 or now.hour > 16:
        s = input("Invalid time range. Please re-enter: ")
        now = get_time(s)

    print("Start time: ", now.strftime("%H:%M:%S"))

    pfs_v = []
    for i in range(4):
        if now.hour + i > 16:
            break
        filename = f"python/post_office_with_info_{now.hour + i}.json"
        gm.from_json(filename)
        pfs_v.append(gm.pfs)

    start = int(input("Enter starting post office code: "))

    num_threads = 4
    threads = []
    outputs = [None] * num_threads

    for thread_id in range(num_threads):
        progress[thread_id] = "Initializing"

    for thread_id in range(num_threads):
        thread = threading.Thread(target=sqa, args=(start, pfs_v, ITER_COUNT, TRY_MAX, outputs, thread_id))
        threads.append(thread)
        thread.start()

    display_thread = threading.Thread(target=display_progress, args=(num_threads,))
    display_thread.start()

    for thread in threads:
        thread.join()

    # Wait for progress display to complete
    display_thread.join()

    print("\nAll threads completed!")
    for output in outputs:
        print(output)

def get_time(s):
    t = datetime.strptime(s, "%H:%M:%S")
    return t.replace(year=2024, month=9, day=11)

if __name__ == "__main__":
    main()
