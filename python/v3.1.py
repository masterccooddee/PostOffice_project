import numpy as np
import json
import random
from datetime import datetime, timedelta
import threading
import time

T0 = 1e6  # Initial temperature
iter_count = 250000  # Iteration count
STAY_TIME = 300  # Default stay time in seconds

# Global variables to track progress
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

def get_time(s):
    t = datetime.strptime(s, "%H:%M:%S")
    return t.replace(year=2024, month=9, day=11)

class OutMsg:
    def __init__(self, message1=None, message2=None, s_r=None, ttime=None, arrive_time=None, benchmark=None):
        self.message1 = message1
        self.message2 = message2
        self.s_r = s_r
        self.ttime = ttime
        self.arrive_time = arrive_time
        self.benchmark = benchmark

def preload_data(input_time):
    gm = GMap()
    now = get_time(input_time)
    pfs_v = {}
    for i in range(4):
        hour = now.hour + i
        if hour > 16:
            break
        filename = f"post_office_with_info_{hour}.json"
        gm.from_json(filename)
        pfs_v[hour] = gm.pfs.copy()
    return pfs_v

def build_time_matrix(pfs):
    size = len(pfs)
    time_matrix = np.full((size, size), np.inf)

    for i in range(size):
        for j, data in pfs[i].info.items():
            time_matrix[i, int(j)] = data[1]  # Travel time

    return time_matrix

def calculate_time_cost(route, time_matrices, current_time):
    total_cost = 0
    now = current_time
    for i in range(len(route) - 1):
        from_city = route[i]
        to_city = route[i + 1]
        hour_index = min(now.hour - 9, len(time_matrices) - 1)
        travel_time = time_matrices[hour_index][from_city][to_city]
        total_cost += travel_time
        now += timedelta(seconds=travel_time + STAY_TIME)
    return total_cost

def extract_route(ct_matrix, start):
    route = []
    for row in ct_matrix:
        for col in range(len(row)):
            if row[col] == 1:
                route.append(col)
                break
    route.append(start)  # Return to start
    if len(set(route)) != len(route) - 1:  # Allow only one duplicate (start point)
        print(f"Invalid path detected: {route}")
    return route

def sqa(input_time, start, output_list, thread_id, time_matrices, num_threads):
    global progress

    seed = random.randint(0, 1000000)
    random.seed(seed)

    num_cities = len(time_matrices[0])
    ct_matrix = [[0 for _ in range(num_cities)] for _ in range(num_cities)]
    for i in range(1, num_cities):
        ct_matrix[i][i] = 1
    ct_matrix[0][start] = 1

    best_time = float('inf')
    shortest_route = []
    max_time = max(np.max(matrix[matrix < np.inf]) for matrix in time_matrices)
    min_time = min(np.min(matrix[matrix > 0]) for matrix in time_matrices)
    alpha = (thread_id / (num_threads - 1)) * max_time + min_time

    print(f"Thread {thread_id} Initial Alpha: {alpha}")
    start_time = time.time()

    for iteration in range(iter_count):
        current_route = extract_route(ct_matrix, start)
        total_cost = calculate_time_cost(current_route, time_matrices, get_time(input_time))

        if total_cost < best_time:
            best_time = total_cost
            shortest_route = current_route
            output_list[thread_id].message1 = (
                f"Iteration {iteration + 1}: Best Route: {shortest_route}, "
                f"Time: {best_time:.2f}s"
            )
            output_list[thread_id].s_r = shortest_route
            output_list[thread_id].ttime = best_time

        # Flip bits randomly (ensure valid routes)
        for i in range(1, num_cities - 1):
            random_city = random.randint(1, num_cities - 2)
            ct_matrix[i] = [0] * num_cities
            ct_matrix[i][random_city] = 1

        with progress_lock:
            progress[thread_id] = f"{iteration + 1}/{iter_count}"

    runtime = time.time() - start_time
    output_list[thread_id] = OutMsg(
        message1=f"Finished. Best Route: {shortest_route}, Best Time: {best_time:.2f}s",
        s_r=shortest_route,
        ttime=runtime,
        benchmark=runtime * best_time
    )
    with progress_lock:
        progress[thread_id] = "Completed"

def display_progress(num_threads):
    global progress
    while True:
        with progress_lock:
            for thread_id in range(num_threads):
                status = progress.get(thread_id, "Not started")
                print(f"{thread_id}: {status}", end=' | ')
            print("\r", end="")
        time.sleep(0.5)
        if all(progress.get(thread_id) == "Completed" for thread_id in range(num_threads)):
            break

if __name__ == "__main__":
    now = None
    print("Welcome to the Postal Route Optimization Program")
    s = input("Enter start time (ex. 12:03:04 or -1 for now): ")

    while True:
        if s == "-1":
            now = datetime.now()
        else:
            now = get_time(s)

        if 9 <= now.hour <= 16:
            break
        print("Invalid time range. Please re-enter: ")
        s = input()

    print("Start time: ", now.strftime("%H:%M:%S"))
    start = int(input("Enter starting post office code: "))
    while not (0 <= start < 16):
        print("Input out of range, please re-enter: ")
        start = int(input())

    num_threads = 4
    threads = []
    outputs = [OutMsg() for _ in range(num_threads)]
    time_matrices = [build_time_matrix(preload_data(s)[hour]) for hour in range(9, 17)]

    for thread_id in range(num_threads):
        progress[thread_id] = "Initializing"
        thread = threading.Thread(target=sqa, args=(s, start, outputs, thread_id, time_matrices, num_threads))
        threads.append(thread)
        thread.start()

    display_thread = threading.Thread(target=display_progress, args=(num_threads,))
    display_thread.start()

    for thread in threads:
        thread.join()
    display_thread.join()

    print("\nAll threads completed!")
    for thread_id, output in enumerate(outputs):
        if output.message1:
            print(f"Thread {thread_id}: {output.message1}")
            print(f"Benchmark: {output.benchmark:.2f}, Runtime: {output.ttime:.2f}s")
        else:
            print(f"Thread {thread_id} failed to complete.")
