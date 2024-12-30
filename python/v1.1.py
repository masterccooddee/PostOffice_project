import json
import random
from datetime import datetime, timedelta
import time

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
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for item in data['post_office']:
                post_office = PostOffice(item['index'], item['name'], item['info'])
                self.pfs[post_office.num] = post_office

def loading(process, total, s=""):
    count = 0
    percent = int(process * 100.0 / total)
    print(f"\r{s} {process} / {total} => {percent}% [", end='')

    for j in range(5, percent + 1, 5):
        print("##", end='')  # Show progress bar
        count += 1

    print(".. " * (20 - count), end='')
    print("]", end='\r')

def get_time(s):
    t = datetime.strptime(s, "%H:%M:%S")
    return t.replace(year=2024, month=9, day=11)

def preload_data(gm, start_hour):
    """
    預加載指定小時範圍內的郵局數據。
    """
    loaded_data = {}
    for hour in range(start_hour, min(start_hour + 4, 17)):  # 確保不超過16點
        filename = f"post_office_with_info_{hour}.json"
        gm.from_json(filename)
        loaded_data[hour] = gm.pfs.copy()  # 深拷貝數據
    return loaded_data

def calculate_time_cost_with_cache(route, gm_data_cache, start_time):
    """
    使用預加載數據計算路徑時間成本。
    """
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

def main():
    gm = GMap()
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

    # 預加載所有可能的郵局數據
    gm_data_cache = preload_data(gm, now.hour)

    # 剩下的程式邏輯保持不變，計算時間時使用 `calculate_time_cost_with_cache`
    pf_vec = list(range(len(gm_data_cache[now.hour])))  # Postal office order
    shortest_vec = []
    s_time_cs = float('inf')
    start = int(input("Enter starting post office code: "))

    while not (0 <= start < len(gm_data_cache[now.hour])):
        print("Input out of range, please re-enter: ")
        start = int(input())

    pf_vec.remove(start)
    pf_vec = [start] + pf_vec + [start] 
    now_vec = pf_vec.copy()

    start_time = time.time()
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

        l_time_cs = calculate_time_cost_with_cache(now_vec, gm_data_cache, now)

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
                y = 1 / (2.71828 ** exp_argument)

        x = random.uniform(0.0, 1.0)

        if y > x:
            shortest_vec = now_vec.copy()
            s_time_cs = l_time_cs
            successful_iterations += 1 

            print(f"\rIteration: {successful_iterations} Temp: {t0:.3f}", end='')
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
    end_time = time.time()

    for i, it in enumerate(shortest_vec):
        if i == 0:
            print(gm_data_cache[now.hour][it].name, end="")
        else:
            print(" ->", gm_data_cache[now.hour][it].name, end="")

    print()

    print("Execution Time:", round(end_time - start_time, 2), "seconds")
    print("benchmark:", round(end_time - start_time, 2) * s_time_cs)

if __name__ == "__main__":
    main()