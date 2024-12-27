import json
import random
from datetime import datetime, timedelta
import threading
import time

T0 = 1e6  # Initial temperature
iter_count = 25000000  # Iteration count
TRY_MAX = int(1.8e6)  # Maximum attempts
STAY_TIME = 300  # Default stay time in seconds

# Global variable to track progress
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
    def __init__(self, message1=None, message2=None, s_r=None, ttime=None, arrive_time=None):
        self.message1 = message1
        self.message2 = message2
        self.s_r = s_r
        self.ttime = ttime
        self.arrive_time = arrive_time


def sa_with_multiple_coefficients(input_time, start, output_list, thread_id):
    global progress

    gm = GMap()
    now = get_time(input_time)

    pfs_v = []
    for i in range(4):
        if now.hour + i > 16:
            break
        filename = f"python/post_office_with_info_{now.hour + i}.json"
        gm.from_json(filename)
        pfs_v.append(gm.pfs)

    pfs = pfs_v[0]

    # Generate random seed
    seed = random.randint(0, 1000000)
    random.seed(seed)

    pf_vec = list(range(len(pfs)))  # Postal office order
    best_vec = []  # Best postal office order
    best_time_cs = float('inf')  # Best travel time

    now_vec = pf_vec.copy()
    now_vec.remove(start)
    now_vec = [start] + now_vec + [start]  # Adding start point at the beginning and end

    # Initialize penalty coefficients
    dmin = min(min(pfs[i].info[str(j)][1] for j in pfs[i].info) for i in pfs)
    dmax = max(max(pfs[i].info[str(j)][1] for j in pfs[i].info) for i in pfs)
    penalty_values = [dmin + (dmax - dmin) * i / 10 for i in range(11)]

    # Iterate over multiple penalty coefficients
    for alpha in penalty_values:
        t0 = T0
        successful_iterations = 0

        for i in range(iter_count):
            if t0 < 1e-2:
                break

            l_time_cs = 0
            for j in range(len(now_vec) - 1):
                travel_time = pfs[now_vec[j]].info[str(now_vec[j + 1])][1]
                l_time_cs += travel_time
                now += timedelta(seconds=travel_time + STAY_TIME)

                if now.hour > (now.hour + j) and now.hour <= 16:
                    pfs = pfs_v[now.hour - 9]

            # Adjust time difference with penalty coefficient
            total_cost = l_time_cs + alpha * (len(set(now_vec)) - len(now_vec))
            if total_cost < best_time_cs:
                best_vec = now_vec.copy()
                best_time_cs = total_cost
                successful_iterations += 1
                t0 *= 0.9  # Cooling schedule

            # Rearrange the path
            first = random.randint(1, len(now_vec) - 2)
            second = random.randint(1, len(now_vec) - 2)
            while first == second:
                second = random.randint(1, len(now_vec) - 2)
            now_vec[first], now_vec[second] = now_vec[second], now_vec[first]

    output_list[thread_id] = OutMsg(
        message1=f"Finish Best Route: {best_vec}, Time: {best_time_cs}s",
        s_r=best_vec,
        ttime=best_time_cs
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

    # Initialize progress dictionary
    for thread_id in range(num_threads):
        progress[thread_id] = "Initializing"

    # Start simulated annealing threads
    for thread_id in range(num_threads):
        thread = threading.Thread(target=sa_with_multiple_coefficients, args=(s, start, outputs, thread_id))
        threads.append(thread)
        thread.start()

    # Start display progress thread
    display_thread = threading.Thread(target=display_progress, args=(num_threads,))
    display_thread.start()

    # Wait for all simulated annealing threads to complete
    for thread in threads:
        thread.join()

    # Wait for display progress thread to complete
    display_thread.join()

    print("\nAll threads completed!")
    for output in outputs:
        if output.message1:
            print(output.message1)
        else:
            print(f"Thread failed to complete.")