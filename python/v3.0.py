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

def sqa(input_time, start, output_list, thread_id, time_matrices, num_threads, gm_data_cache):
    global progress

    # 初始化隨機種子
    seed = random.randint(0, 1000000)
    random.seed(seed)

    # 初始化量子態矩陣 (route matrix)
    num_cities = len(time_matrices[0])
    ct_matrix = [[0 for _ in range(num_cities)] for _ in range(num_cities)]
    for i in range(num_cities):
        ct_matrix[i][i] = 1
    ct_matrix[0][start] = 1

    best_time = float('inf')  # 最佳解的時間成本
    shortest_route = []  # 最佳路徑

    # 動態計算 alpha
    max_time = max(np.max(matrix[matrix < np.inf]) for matrix in time_matrices)
    min_time = min(np.min(matrix[matrix > 0]) for matrix in time_matrices)

    alpha_coff = thread_id / (num_threads - 1)
    alpha = alpha_coff * max_time + min_time

    print(f"Thread {thread_id} Initial Alpha: {alpha}")

    start_time = time.time()

    for iteration in range(iter_count):
        # 選擇對應的時間矩陣
        current_hour = get_time(input_time).hour
        time_matrix = time_matrices[min(current_hour - 9, len(time_matrices) - 1)]

        # 計算時間成本與懲罰項
        total_cost_time, depart_time, h1, h2 = calculate_time_cost(ct_matrix, time_matrices, get_time(input_time), alpha)
        total_cost = total_cost_time + alpha * (h1 + h2)
        
        if total_cost < best_time:
            best_time = total_cost
            true_cost = total_cost_time
            shortest_route = extract_route(ct_matrix, start)

            output_list[thread_id].message1 = (f"Iteration {iteration + 1}: Best Route: {shortest_route}, "
                                               f"Time: {best_time:.2f}s, Departure: {depart_time}")
            output_list[thread_id].s_r = shortest_route
            output_list[thread_id].ttime = best_time

        # 隨機翻轉比特（更新量子態）
        for i in range(1, num_cities):
            random_city = random.randint(0, num_cities - 1)
            ct_matrix[i] = [0] * num_cities
            ct_matrix[i][random_city] = 1

        # 更新進度
        with progress_lock:
            progress[thread_id] = f"{iteration + 1}/{iter_count}"

    end_time = time.time()
    runtime = end_time - start_time

    output_list[thread_id] = OutMsg(
        message1=f"Finished. Best Route: {shortest_route}, Best Time: {best_time:.2f}s, True cost: {true_cost:.2f}",
        s_r=shortest_route,
        ttime=runtime,
        benchmark=runtime * best_time
    )

    with progress_lock:
        progress[thread_id] = "Completed"

def calculate_time_cost(route_matrix, time_matrices, current_time, alpha):
    total_cost = 0
    h1 = 0  # 懲罰項：每個城市被訪問一次
    h2 = 0  # 懲罰項：每個時間段僅訪問一次

    num_cities = len(route_matrix)
    visit_count = [0] * num_cities

    for i in range(len(route_matrix)):
        for j in range(len(route_matrix[i])):
            if route_matrix[i][j] == 1:
                visit_count[j] += 1

    h1 = sum((count - 1) ** 2 for count in visit_count)

    for i in range(len(route_matrix)):
        h2 += (sum(route_matrix[i]) - 1) ** 2

    # 計算實際的路徑時間成本
    for i in range(len(route_matrix) - 1):
        for j in range(len(route_matrix[i])):
            if route_matrix[i][j] == 1:
                for k in range(len(route_matrix[i + 1])):
                    if route_matrix[i + 1][k] == 1:
                        total_cost += time_matrices[current_time.hour - 9][j][k]

    return total_cost, current_time, h1, h2

def extract_route(route_matrix, start):
    route = []
    for row in route_matrix:
        for col in range(len(row)):
            if row[col] == 1:
                route.append(col)
                break
    route.append(start)  # 回到起點
    return route

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

    for thread_id in range(num_threads):
        progress[thread_id] = "Initializing"

    for thread_id in range(num_threads):
        thread = threading.Thread(target=sqa, args=(s, start, outputs, thread_id, time_matrices, num_threads, gm_data_cache))
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