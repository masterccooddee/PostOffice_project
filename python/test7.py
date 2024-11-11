#one thread printing process

import json
import random
from datetime import datetime, timedelta
import multiprocessing
import math
import copy  # Added for deep copying pfs

T0 = 1e6  # Initial temperature
iter_count = 2500000000 
TRY_MAX = int(1.8e6)  # Maximum attempts
STAY_TIME = 300  # Default stay time in seconds
cooling_rate = 0.9
thread_num = 1

###測試用
def loading(process, total, s=""):
    count = 0
    percent = int(process * 100.0 / total)
    print(f"\r{s} {process} / {total} => {percent}% [", end='')

    for j in range(5, percent + 1, 5):
        print("##", end='')  # Show progress bar
        count += 1

    print(".. " * (20 - count), end='')
    print("]", end='\r')

class PostOffice:
    def __init__(self, num, name, info):
        self.num = num
        self.name = name
        self.info = info

class GMap:
    def __init__(self):
        self.pfs = {}

    def from_json(self, filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data['post_office']:
                    post_office = PostOffice(item['index'], item['name'], item['info'])
                    self.pfs[post_office.num] = post_office
        except Exception as e:
            print(f"Error loading {filename}: {e}")

def get_time(s):
    t = datetime.strptime(s, "%H:%M:%S")
    return t.replace(year=2024, month=9, day=11)

def simulated_annealing(gm, start, now, pfs_v):
    pf_vec = list(range(len(gm.pfs)))  # Postal office order
    shortest_vec = []  # Shortest postal office order
    s_time_cs = float('inf')  # Shortest travel time

    pf_vec.remove(start)
    pf_vec = [start] + pf_vec + [start]  # Establish postal office order
    now_vec = pf_vec.copy()

    # Simulated annealing algorithm
    t0 = T0
    try_cnt = 1
    successful_iterations = 0  # Initialize the successful iterations counter

    for i in range(iter_count):
        if try_cnt > TRY_MAX:
            print(f"\nTried {TRY_MAX} times!!!!")
            break

        if t0 < 1e-2:
            print("Temperature is too low!")
            break

        l_time_cs = 0

        # Calculate total time for this combination
        for j in range(len(now_vec) - 1):
            travel_time = gm.pfs[now_vec[j]].info[str(now_vec[j + 1])][1]  # Get travel time
            l_time_cs += travel_time
            now += timedelta(seconds=travel_time + STAY_TIME)  # Update time including stay time

            # Check if we need to switch to the next hourly post office data
            if now.hour > (now.hour + j) and now.hour <= 16:
                pfs = pfs_v[now.hour - 9]

        # Simulated annealing acceptance criterion
        if l_time_cs < s_time_cs:
            y = 1
        else:
            time_diff = l_time_cs - s_time_cs
            # Limit time difference
            if time_diff > 700:
                time_diff = 700
            elif time_diff < -700:
                time_diff = -700

            if t0 <= 1e-10:
                print("Temperature is too low, adjusting to minimum value.")
                t0 = 1e-10

            # Ensure time_diff / t0 does not exceed a threshold
            exp_argument = time_diff / t0
            if exp_argument > 709:  # Limiting to avoid overflow
                y = 0
            elif exp_argument < -709:
                y = 1
            else:
                y = 1 / (2.71828 ** exp_argument)

        x = random.uniform(0.0, 1.0)

        if y > x:
            shortest_vec = now_vec.copy()
            s_time_cs = l_time_cs
            successful_iterations += 1  # Increment successful iteration counter
            print(f"\rIteration: {successful_iterations} Temp: {t0:.3f}", end='')  # Show successful iterations
            print("Now:", now_vec, "Shortest:", shortest_vec, "Time cost:", s_time_cs)
            print("=" * 100)

            t0 *= cooling_rate  # Cooling schedule
            try_cnt = 0
        else:
            i -= 1
            now_vec = shortest_vec.copy()
            loading(try_cnt, TRY_MAX, "Trying, please wait...")
            try_cnt += 1

        # Randomly rearrange the path
        first = random.randint(1, len(now_vec) - 2)
        second = random.randint(1, len(now_vec) - 2)
        while first == second:
            second = random.randint(1, len(now_vec) - 2)
        now_vec[first], now_vec[second] = now_vec[second], now_vec[first]

    print(f"Successful iterations: {successful_iterations}")
    return s_time_cs, shortest_vec

def parallel_simulation(gm, seed, pfs_v, start, now):
    print(f"Running simulation for seed {seed}...")
    random.seed(seed)  # Use seed for random number generation
    result = simulated_annealing(gm, start, now, pfs_v)
    return result


def main():
    gm = GMap()
    now = None

    print("Welcome to the Postal Route Optimization Program")
    s = input("Enter start time (ex. 12:03:04 or -1 for now): ")

    # Time validation
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

    # Load post office data
    pfs_v = []
    for i in range(thread_num):
        if now.hour + i > 16:
            break
        filename = f"python/post_office_with_info_{now.hour + i}.json"
        gm.from_json(filename)
        pfs_v.append(copy.deepcopy(gm.pfs))  # Use deepcopy to avoid reference issues

    seeds = [random.randint(0, int(1e6)) for _ in range(thread_num)]
    
    start = int(input("Enter starting post office code: "))
    while not (0 <= start < len(gm.pfs)):
        print("Input out of range, please re-enter: ")
        start = int(input())

    # Call the parallel simulation function with gm as an argument
    with multiprocessing.Pool(processes=thread_num) as pool:
        results = pool.starmap(parallel_simulation, [(gm, seed, pfs_v, start, now) for seed in seeds])
    
    # Process results (this part is unchanged)
    for result in results:
        shortest_time, shortest_path = result
        print("\nShortest Time:", shortest_time)
        print("Path:")
        for i, it in enumerate(shortest_path):
            if i == 0:
                print(gm.pfs[it].name, end="")  # No arrow before the first element (starting point)
            else:
                print(" ->", gm.pfs[it].name, end="")  # Add arrow before subsequent elements

    print()  # Print newline after the path

if __name__ == "__main__":
    main()

