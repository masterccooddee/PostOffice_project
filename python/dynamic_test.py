import numpy as np
import json
import random
from datetime import datetime, timedelta
import threading
import time

T0 = 1e6  # Initial temperature
iter_count = 250000  # Iteration count
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
        return self

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

def make_matrix(post_offices):
    N = len(post_offices)
    time_matrix = np.zeros((N, N), dtype=int)

    for i in range(N):
        for j in range(N):
            if i == j:
                time_matrix[i][j] = 0
            else:
                try:
                    time_matrix[i][j] = post_offices[i].info[str(j)][1]
                except KeyError:
                    time_matrix[i][j] = np.inf

    return time_matrix

def time_cost(route, dis_matrices, current_time, alpha):
    time_cost = 0
    h1 = 0
    h2 = 0
    initial_time = current_time

    visit_counts = [0] * len(dis_matrices[0])

    for i in range(len(route) - 1):
        from_node = int(route[i])
        to_node = int(route[i + 1])

        time_index = min(max(0, current_time.hour - initial_time.hour), len(dis_matrices) - 1)
        travel_time = dis_matrices[time_index][from_node, to_node]

        time_cost += travel_time
        visit_counts[from_node] += 1

        current_time += timedelta(seconds=travel_time + STAY_TIME)

    visit_counts[route[-1]] += 1

    h1 = sum((count - 1) ** 2 for count in visit_counts if count > 1)
    h2 = sum(1 for count in visit_counts if count == 0)

    total_cost = time_cost + alpha * (h1 + h2)
    return total_cost, current_time, h1, h2

def SQA(input_time, start, iter_time, t_matrix_slice, msg, thread_id, alpha_coff):
    try:
        now_time = datetime.now() if input_time == "-1" else datetime.strptime(input_time, "%H:%M:%S").replace(year=2024, month=12, day=25)
        
        t_max = max(np.max(matrix) for matrix in t_matrix_slice)
        t_min = min(np.min(matrix[matrix > 0]) for matrix in t_matrix_slice)
        assert t_min > 0, "Minimum travel time must be positive"
        epson = float(t_min)

        N = len(t_matrix_slice[0])
        ct_matrix = np.zeros((N, N), dtype=int)
        ct_matrix[0, start] = 1

        best_time = float('inf')
        alpha = alpha_coff * t_max + epson
        start_timestamp = time.time()

        for iteration in range(iter_time):
            elapsed = int(time.time() - start_timestamp)
            minutes, seconds = divmod(elapsed, 60)
            msg[thread_id].message2 = f"\rTrying {iteration+1}/{iter_time}  {((iteration+1)*100)//iter_time}% [{minutes:02}:{seconds:02}]"

            t_c, depart, h1, h2 = time_cost(list(range(N)), t_matrix_slice, now_time, alpha)

            if t_c < best_time:
                best_time = t_c
                msg[thread_id].arrive_time = depart.strftime("%I:%M:%S %p")
                msg[thread_id].ttime = int(t_c)
                msg[thread_id].s_r = list(range(N))
                msg[thread_id].message1 = (
                    f"\rIteration {iteration+1} Alpha: {alpha:.3f} Epsilon: {epson:.3f} "
                    f"Route: {msg[thread_id].s_r} Time: {int(t_c)}s \U0001F69B {msg[thread_id].arrive_time}"
                )

            for j in range(1, N):
                random_walk = random.randint(0, N - 1)
                ct_matrix[j] = np.zeros(N, dtype=int)
                ct_matrix[j, random_walk] = 1

    except Exception as e:
        print(f"Thread {thread_id} encountered an error: {e}")
        with progress_lock:
            progress[thread_id] = "Error"

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

    t_matrix_slice = []
    for hour_offset in range(4):
        current_hour = now.hour + hour_offset
        if current_hour > 16:
            break
        filename = f"post_office_with_info_{current_hour}.json"
        gm = GMap().from_json(filename)
        t_matrix_slice.append(make_matrix(gm.pfs))

    print("Loaded Time Matrices")

    for thread_id in range(num_threads):
        progress[thread_id] = "Initializing"

    for thread_id in range(num_threads):
        thread = threading.Thread(target=SQA, args=(s, start, iter_count, t_matrix_slice, outputs, thread_id, 0.5))
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
