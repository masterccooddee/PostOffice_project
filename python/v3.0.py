import numpy as np
import json
import random
from datetime import datetime, timedelta
import threading
import time

T0 = 1e6  # Initial temperature
iter_count = 25000000  # Iteration count
TRY_MAX = int(1.8e6)  # Maximum attempts
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

def calculate_time_cost_with_cache(route, gm_data_cache, start_time):
    total_cost_time = 0
    now = start_time

    for i in range(len(route) - 1):
        from_pfs = route[i]
        to_pfs = route[i + 1]

        current_pfs = gm_data_cache[now.hour]  # 從緩存中獲取當前小時的數據
        travel_data = current_pfs[from_pfs].info[str(to_pfs)]
        travel_distance, travel_time = travel_data

        total_cost_time += travel_time
        now += timedelta(seconds=travel_time + STAY_TIME)

    return total_cost_time

def build_time_matrix(pfs):
    size = len(pfs)
    time_matrix = np.full((size, size), np.inf)

    for i in range(size):
        for j, data in pfs[i].info.items():
            time_matrix[i, int(j)] = data[1]  # Travel time

    return time_matrix

def sa(input_time, start, output_list, thread_id, time_matrices, num_threads, gm_data_cache):
    global progress

    # Generate random seed
    seed = random.randint(0, 1000000)
    random.seed(seed)

    pf_vec = list(range(len(time_matrices[0])))  # Postal office order
    shortest_vec = []  # Shortest postal office order
    s_time_cs = float('inf')  # Shortest travel time

    # Establish postal office order
    now_vec = pf_vec.copy()
    now_vec.remove(start)
    now_vec = [start] + now_vec + [start]  # Adding start point at the beginning and end

    # Calculate dynamic alpha
    max_time = max(np.max(matrix[matrix < np.inf]) for matrix in time_matrices)
    min_time = min(np.min(matrix[matrix > 0]) for matrix in time_matrices)

    alpha_coff = thread_id / (num_threads - 1)
    alpha = alpha_coff * max_time + min_time

    print(f"Thread {thread_id} Initial Alpha: {alpha}")

    t0 = T0
    try_cnt = 1
    successful_iterations = 0

    start_time = time.time()

    for i in range(iter_count):
        if try_cnt > TRY_MAX:
            output_list[thread_id].message1 = f"\nTried {TRY_MAX} times!!!!"
            break

        if t0 < 1e-2:
            output_list[thread_id].message1 = "Temperature is too low!"
            break

        # Select the appropriate matrix based on time
        current_hour = get_time(input_time).hour
        time_matrix = time_matrices[min(current_hour - 9, len(time_matrices) - 1)]

        # Calculate current route cost
        total_cost_time = calculate_time_cost_with_cache(now_vec, gm_data_cache, get_time(input_time))

        # Add penalties
        visit_count = np.bincount(now_vec, minlength=len(time_matrix))
        h1 = np.sum((visit_count - 1) ** 2)
        total_cost_with_penalty = total_cost_time + alpha * h1

        # Simulated annealing acceptance criterion
        if total_cost_with_penalty < s_time_cs:
            y = 1
        else:
            time_diff = total_cost_with_penalty - s_time_cs
            time_diff = max(min(time_diff, 700), -700)

            exp_argument = time_diff / t0
            y = 1 / (2.71828 ** exp_argument) if -709 < exp_argument < 709 else (1 if exp_argument < -709 else 0)

        x = random.uniform(0.0, 1.0)

        if y > x:
            shortest_vec = now_vec.copy()
            s_time_cs = total_cost_with_penalty
            successful_iterations += 1

            # Calculate shortest distance without penalties
            shortest_distance = calculate_time_cost_with_cache(shortest_vec, gm_data_cache, get_time(input_time))

            output_list[thread_id].message1 = f"Finish Shortest Route: {shortest_vec}, Time cost with penalty: {s_time_cs}s, Distance without penalty: {shortest_distance}s"
            output_list[thread_id].message2 = f"Now: {now_vec} Shortest: {shortest_vec}"

            t0 *= 0.9
            try_cnt = 0
        else:
            i -= 1
            now_vec = shortest_vec.copy()
            with progress_lock:
                progress[thread_id] = f"{try_cnt}/{TRY_MAX}"
            try_cnt += 1

        # Randomly rearrange the path
        first = random.randint(1, len(now_vec) - 2)
        second = random.randint(1, len(now_vec) - 2)
        while first == second:
            second = random.randint(1, len(now_vec) - 2)
        now_vec[first], now_vec[second] = now_vec[second], now_vec[first]

    end_time = time.time()
    runtime = end_time - start_time
    benchmark = runtime * s_time_cs

    output_list[thread_id] = OutMsg(
        message1=f"Finish Shortest Route: {shortest_vec}, Time cost with penalty: {s_time_cs}s, Distance without penalty: {shortest_distance}s",
        s_r=shortest_vec,
        ttime=runtime,
        benchmark=benchmark
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
        print("Start at: ", start)

    time.sleep(0.5)

    num_threads = 4
    threads = []
    outputs = [OutMsg() for _ in range(num_threads)]

    pfs_v = preload_data(s)
    time_matrices = [build_time_matrix(pfs) for _, pfs in pfs_v.items()]

    gm_data_cache = preload_data(s)

    print("Time Matrices:")
    for hour, matrix in zip(range(9, 9 + len(time_matrices)), time_matrices):
        print(f"Hour {hour}:")
        print(matrix)

    for thread_id in range(num_threads):
        progress[thread_id] = "Initializing"

    for thread_id in range(num_threads):
        thread = threading.Thread(target=sa, args=(s, start, outputs, thread_id, time_matrices, num_threads, gm_data_cache))
        threads.append(thread)
        thread.start()

    # Start progress display thread
    display_thread = threading.Thread(target=display_progress, args=(num_threads,))
    display_thread.start()

    # Wait for all simulated annealing threads to complete
    for thread in threads:
        thread.join()

    # Wait for progress display thread to complete
    display_thread.join()

    print("\nAll threads completed!")
    for thread_id, output in enumerate(outputs):
        if output.message1:
            print(f"Thread {thread_id}: {output.message1}")
            print(f"Benchmark: {output.benchmark:.2f}, Runtime: {output.ttime:.2f}s")
        else:
            print(f"Thread {thread_id} failed to complete.")