import json
import random
from datetime import datetime, timedelta
import multiprocessing
import math

T0 = 1e5  # Initial temperature
iter_count = 2500000000  # Reduced for practical simulation
TRY_MAX = int(1.8e6)  # Maximum attempts
STAY_TIME = 300  # Default stay time in seconds
cooling_rate = 0.97

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

def simulated_annealing(gm, start, now, pfs_v, seed):
    # Initialize random seed for each process
    random.seed(seed)

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
        current_time = now  # Use a separate variable to avoid time modification issues
        for j in range(len(now_vec) - 1):
            travel_time = gm.pfs[now_vec[j]].info[str(now_vec[j + 1])][1]  # Get travel time
            l_time_cs += travel_time
            current_time += timedelta(seconds=travel_time + STAY_TIME)  # Update time including stay time

            # Check if we need to switch to the next hourly post office data
            if current_time.hour > (now.hour + j) and current_time.hour <= 16:
                pfs = pfs_v[current_time.hour - 9]

        # Simulated annealing acceptance criterion
        if l_time_cs < s_time_cs:
            shortest_vec = now_vec.copy()
            s_time_cs = l_time_cs
            successful_iterations += 1  # Increment successful iteration counter
            t0 *= cooling_rate  # Cooling schedule
            try_cnt = 0
        else:
            x = random.uniform(0.0, 1.0)
            time_diff = l_time_cs - s_time_cs
            y = math.exp(-time_diff / t0) if time_diff > 0 else 1

            if y > x:
                shortest_vec = now_vec.copy()
                s_time_cs = l_time_cs
                successful_iterations += 1  # Increment successful iteration counter
                t0 *= cooling_rate  # Cooling schedule
                try_cnt = 0
            else:
                i -= 1
                now_vec = shortest_vec.copy()
                try_cnt += 1

        # Randomly rearrange the path
        first = random.randint(1, len(now_vec) - 2)
        second = random.randint(1, len(now_vec) - 2)
        while first == second:
            second = random.randint(1, len(now_vec) - 2)
        now_vec[first], now_vec[second] = now_vec[second], now_vec[first]

    return s_time_cs, shortest_vec


def parallel_simulation(gm, seed, pfs_v, start, now):
    print(f"Running simulation for seed {seed}...")
    result = simulated_annealing(gm, start, now, pfs_v, seed)
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
    for i in range(4):
        if now.hour + i > 16:
            break
        filename = f"python/post_office_with_info_{now.hour + i}.json"
        gm.from_json(filename)
        pfs_v.append(gm.pfs)

    seeds = [random.randint(0, int(1e6)) for _ in range(4)]
    
    start = int(input("Enter starting post office code: "))
    while not (0 <= start < len(gm.pfs)):
        print("Input out of range, please re-enter: ")
        start = int(input())

    # Call the parallel simulation function with gm as an argument
    with multiprocessing.Pool(processes=4) as pool:
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