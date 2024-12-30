###距離檢查工具

import json
from datetime import datetime, timedelta

STAY_TIME = 300

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

def calculate_time_cost(route, gm, now):
    total_cost_time = 0
    total_cost_distance = 0

    print("Starting calculation...")
    for i in range(len(route) - 1):
        from_pfs = route[i]
        to_pfs = route[i + 1]

        filename = f"python/post_office_with_info_{now.hour}.json"
        print(f"Loading data for hour: {now.hour}, from file: {filename}")
        gm.from_json(filename)
        current_pfs = gm.pfs

        travel_data = current_pfs[from_pfs].info[str(to_pfs)]
        travel_distance, travel_time = travel_data

        total_cost_distance += travel_distance
        total_cost_time += travel_time

        now += timedelta(seconds=travel_time + STAY_TIME)

        print(f"From Post Office {from_pfs} to {to_pfs}: +{travel_distance} meters, +{travel_time} seconds")
        print(f"Stay Time: +{STAY_TIME} seconds")
        print(f"Current Time: {now.strftime('%H:%M:%S')}")

    print(f"Total Distance: {total_cost_distance} meters")
    print(f"Total Travel Time: {total_cost_time} seconds")
    return total_cost_time

def quick_calculate_distance(route, gm, start_time):
    now = start_time  # Use the provided start time
    total_distance = calculate_time_cost(route, gm, now)
    return total_distance

def main():
    gm = GMap()
    now = None

    print("Welcome to the Quick Distance Calculator")
    s = input("Enter start time (ex. 12:03:04 or -1 for now): ")

    if s == "-1":
        now = datetime.now()
    else:
        now = get_time(s)

    while now.hour < 9 or now.hour > 16:
        s = input("Invalid time range. Please re-enter: ")
        now = get_time(s)

    print("Start time: ", now.strftime("%H:%M:%S"))

    route = list(map(int, input("Enter the route as space-separated post office IDs: ").split()))
    total_time = quick_calculate_distance(route, gm, now)

    if total_time is not None:
        print("\nTotal Travel Time:", total_time, "seconds")
    else:
        print("Calculation failed due to missing data.")

if __name__ == "__main__":
    main()
