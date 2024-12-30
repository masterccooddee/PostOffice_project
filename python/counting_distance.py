import json
from datetime import datetime, timedelta

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

def get_time(s):
    t = datetime.strptime(s, "%H:%M:%S")
    return t.replace(year=2024, month=9, day=11)

def calculate_time_cost(route, pfs_v, now):
    total_cost = 0
    current_pfs = pfs_v[0]

    for i in range(len(route) - 1):
        from_pfs = route[i]
        to_pfs = route[i + 1]
        travel_time = current_pfs[from_pfs].info[str(to_pfs)][1]
        total_cost += travel_time
        now += timedelta(seconds=travel_time + STAY_TIME)

        # Update the time-based post office data
        if now.hour > 9 and now.hour <= 16:
            current_pfs = pfs_v[now.hour - 9]

    return total_cost

def quick_calculate_distance(route, pfs_v):
    now = datetime(2024, 9, 11, 9, 0, 0)  # Default start time
    total_distance = calculate_time_cost(route, pfs_v, now)
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

    pfs_v = []
    for i in range(4):
        if now.hour + i > 16:
            break
        filename = f"python/post_office_with_info_{now.hour + i}.json"
        gm.from_json(filename)
        pfs_v.append(gm.pfs)

    route = list(map(int, input("Enter the route as space-separated post office IDs: ").split()))
    total_time = quick_calculate_distance(route, pfs_v)

    print("\nTotal Travel Time:", total_time, "seconds")

if __name__ == "__main__":
    main()