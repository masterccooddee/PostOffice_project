import json
import random
from datetime import datetime, timedelta

T0 = 1e6  # Initial temperature
iter_count = 2500000000000  # Iteration count
TRY_MAX = int(1.8e6)  # Maximum attempts
STAY_TIME = 300  # Default stay time in seconds


class PostOffice:
    def __init__(self, num, name, info):
        self.num = num
        self.name = name
        self.info = info


class GMap:
    def __init__(self):
        self.pfs = {}

    def from_json(self, filename):
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
            for item in data["post_office"]:
                post_office = PostOffice(item["index"], item["name"], item["info"])
                self.pfs[post_office.num] = post_office


def loading(process, total, s=""):
    count = 0
    percent = int(process * 100.0 / total)
    print(f"\r{s} {process} / {total} => {percent}% [", end="")

    for j in range(5, percent + 1, 5):
        print("##", end="")  # Show progress bar
        count += 1

    print(".. " * (20 - count), end="")
    print("]", end="\r")


def get_time(s):
    t = datetime.strptime(s, "%H:%M:%S")
    return t.replace(year=2024, month=9, day=11)


def calculate_time_cost(route, gm, start_time):
    total_cost_time = 0
    now = start_time

    for i in range(len(route) - 1):
        from_pfs = route[i]
        to_pfs = route[i + 1]

        # Load post office data based on current hour
        filename = f"post_office_with_info_{now.hour}.json"
        gm.from_json(filename)
        current_pfs = gm.pfs

        travel_data = current_pfs[from_pfs].info[str(to_pfs)]
        travel_distance, travel_time = travel_data

        total_cost_time += travel_time
        now += timedelta(seconds=travel_time + STAY_TIME)

    return total_cost_time


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

    pfs = pfs_v[0]

    seed = random.randint(0, 1000000)
    print("Seed:", seed)
    random.seed(seed)

    pf_vec = list(range(len(pfs)))  # Postal office order
<<<<<<< HEAD
    shortest_vec = []
    s_time_cs = float('inf')
=======
    shortest_vec = []  # Shortest postal office order
    s_time_cs = float("inf")  # Shortest travel time
>>>>>>> 965fd9d2fb5a7519a388b87c1de8a055fb5c349e
    start = int(input("Enter starting post office code: "))

    while not (0 <= start < len(pfs)):
        print("Input out of range, please re-enter: ")
        start = int(input())

    pf_vec.remove(start)
    pf_vec = [start] + pf_vec + [start] 
    now_vec = pf_vec.copy()

    # Simulated annealing algorithm
    t0 = T0
    try_cnt = 1
    successful_iterations = 0

    for i in range(iter_count):
        if try_cnt > TRY_MAX:
            print(f"\nTried {TRY_MAX} times!!!!")
            break

        if t0 < 1e-2:
            print("Temperature is too low!")
            break

        l_time_cs = calculate_time_cost(now_vec, gm, now)

        if l_time_cs < s_time_cs:
            y = 1
        else:
            time_diff = l_time_cs - s_time_cs
            if time_diff > 700:
                time_diff = 700
            elif time_diff < -700:
                time_diff = -700

            if t0 <= 1e-10:
                print("Temperature is too low, adjusting to minimum value.")
                t0 = 1e-10

            exp_argument = time_diff / t0
            if exp_argument > 709:
                y = 0
            elif exp_argument < -709:
                y = 1
            else:
                y = 1 / (2.71828**exp_argument)

        x = random.uniform(0.0, 1.0)

        if y > x:
            shortest_vec = now_vec.copy()
            s_time_cs = l_time_cs
            successful_iterations += 1 

<<<<<<< HEAD
            print(f"\rIteration: {successful_iterations} Temp: {t0:.3f}", end='')
=======
            print(
                f"\rIteration: {successful_iterations} Temp: {t0:.3f}", end=""
            )  # Show successful iterations
>>>>>>> 965fd9d2fb5a7519a388b87c1de8a055fb5c349e
            print("Now:", now_vec, "Shortest:", shortest_vec, "Time cost:", s_time_cs)
            print("=" * 100)

            t0 *= 0.9
            try_cnt = 0
        else:
            i -= 1
            now_vec = shortest_vec.copy()
            loading(try_cnt, TRY_MAX, "Trying, please wait...")
            try_cnt += 1

        first = random.randint(1, len(now_vec) - 2)
        second = random.randint(1, len(now_vec) - 2)
        while first == second:
            second = random.randint(1, len(now_vec) - 2)
        now_vec[first], now_vec[second] = now_vec[second], now_vec[first]

    print("\nShortest Time:", s_time_cs)
    print("Path:")

    for i, it in enumerate(shortest_vec):
        if i == 0:
<<<<<<< HEAD
            print(pfs[it].name, end="")
=======
            print(
                pfs[it].name, end=""
            )  # No arrow before the first element (starting point)
>>>>>>> 965fd9d2fb5a7519a388b87c1de8a055fb5c349e
        else:
            print(" ->", pfs[it].name, end="")

    print()

    total_runtime = calculate_time_cost(shortest_vec, gm, now)
    print("Total Runtime (including stops):", total_runtime, "seconds")
<<<<<<< HEAD
    print("benchmark:", total_runtime * s_time_cs)
    
=======


>>>>>>> 965fd9d2fb5a7519a388b87c1de8a055fb5c349e
if __name__ == "__main__":
    main()
