import json
import random
from datetime import datetime, timedelta
import threading
import time

T0 = 1e6  # Initial temperature
iter_count = 2500  # Iteration count
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

class OutMsg:
    def __init__(self, message1=None, message2=None, s_r=None, ttime=None, arrive_time=None):
        self.message1 = message1
        self.message2 = message2
        self.s_r = s_r
        self.ttime = ttime
        self.arrive_time = arrive_time

def sa(input_time, start, output_list, thread_id):
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
    shortest_vec = []  # Shortest postal office order
    s_time_cs = float('inf')  # Shortest travel time

    # Establish postal office order
    now_vec = pf_vec.copy()
    now_vec.remove(start)
    now_vec = [start] + now_vec + [start]  # Adding start point at the beginning and end

    # Simulated annealing algorithm
    t0 = T0
    try_cnt = 1
    successful_iterations = 0  # Initialize the successful iterations counter

    for i in range(iter_count):
        if try_cnt > TRY_MAX:
            output_list[thread_id].message1 = f"\nTried {TRY_MAX} times!!!!"
            break

        if t0 < 1e-2:
            output_list[thread_id].message1 = "Temperature is too low!"
            break

        l_time_cs = 0

        # Calculate total time for this combination
        for j in range(len(now_vec) - 1):
            travel_time = pfs[now_vec[j]].info[str(now_vec[j + 1])][1]  # Get travel time
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
            # 限制時間差
            if time_diff > 700:
                time_diff = 700
            elif time_diff < -700:
                time_diff = -700

            if t0 <= 1e-10:
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

            output_list[thread_id].message1 = f"Iteration: {successful_iterations} Temp: {t0:.3f}"
            output_list[thread_id].message2 = f"Now: {now_vec} Shortest: {shortest_vec} Time cost: {s_time_cs}s"
            output_list[thread_id].arrive_time = now.strftime("%I:%M:%S %p")

            t0 *= 0.9  # Cooling schedule
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

    output_list[thread_id] = OutMsg(
        message1=f"Finish Shortest Route: {shortest_vec}, Time: {s_time_cs}s",
        s_r=shortest_vec,
        ttime=s_time_cs
    )


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

    for thread_id in range(num_threads):
        thread = threading.Thread(target=sa, args=(s, start, outputs, thread_id))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    print("\n")
    for output in outputs:
        if output.message1:
            print(output.message1)
        else:
            print(f"Thread {thread_id} failed to complete.")
