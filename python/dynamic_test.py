import json
import random
from datetime import datetime, timedelta
import time


def load_data(file_name):
    """Load JSON data from the given file."""
    with open(file_name, 'r') as file:
        data = json.load(file)
    return data


def make_matrix(file_name):
    """Create a time cost matrix from the JSON file."""
    data = load_data(file_name)
    post_offices = data["post_office"]
    n = len(post_offices)
    time_matrix = [[0 if i == j else post_offices[i]["info"][str(j)][1] for j in range(n)] for i in range(n)]
    return time_matrix


def find_max_min(matrices):
    """Find the maximum and minimum time costs across all matrices."""
    times = []
    for matrix in matrices:
        for i in range(len(matrix)):
            for j in range(len(matrix)):
                if i != j:
                    times.append(matrix[i][j])
    return max(times), min(times)


def calculate_time_cost_with_penalty(route, dis_matrices, start_time, alpha):
    """Calculate the total time cost and penalties for a route."""
    total_cost = 0
    now = start_time

    for i in range(len(route) - 1):
        from_idx = route[i]
        to_idx = route[i + 1]
        matrix_idx = min(now.hour - start_time.hour, len(dis_matrices) - 1)
        travel_time = dis_matrices[matrix_idx][from_idx][to_idx]

        total_cost += travel_time
        now += timedelta(seconds=travel_time)

    # Penalty calculations
    visit_count = [0] * len(dis_matrices[0])
    for node in route:
        visit_count[node] += 1

    penalty_h1 = sum((count - 1) ** 2 for count in visit_count)
    penalty_h2 = sum((visit_count[i] - 1) ** 2 for i in range(len(visit_count)))

    total_cost_with_penalty = total_cost + alpha * (penalty_h1 + penalty_h2)

    print(f"Energy Function: Time Cost = {total_cost}, Penalty H1 = {penalty_h1}, Penalty H2 = {penalty_h2}, Total = {total_cost_with_penalty}")

    return total_cost_with_penalty, now, penalty_h1, penalty_h2


def simulated_annealing(input_time, start, iterations, dis_matrices, alpha_coeff):
    """Simulated Annealing Algorithm for route optimization."""
    hour, minute, second = map(int, input_time.split(":"))
    start_time = datetime(2024, 12, 25, hour, minute, second)

    n = len(dis_matrices[0])
    route = list(range(n))
    random.shuffle(route)

    best_time = float('inf')
    best_route = None
    alpha = alpha_coeff * max(find_max_min(dis_matrices))

    for iteration in range(iterations):
        total_cost, new_time, h1, h2 = calculate_time_cost_with_penalty(route, dis_matrices, start_time, alpha)

        if total_cost < best_time:
            best_time = total_cost
            best_route = route.copy()

        # Randomly modify the route (flip two nodes)
        i, j = random.sample(range(1, n), 2)
        route[i], route[j] = route[j], route[i]

    return best_route, best_time


def preload_data(input_time):
    """Preload all postal office data into memory to avoid repeated file reads."""
    gm_data_cache = {}
    hour = int(input_time.split(":")[0])

    for offset in range(4):
        current_hour = hour + offset
        if current_hour > 16:
            break

        file_name = f"data/post_office_with_info_{current_hour}.json"
        try:
            gm_data_cache[current_hour] = make_matrix(file_name)
        except FileNotFoundError:
            break

    return gm_data_cache


def main():
    input_time = input("Enter start time (HH:MM:SS, or -1 for current time): ")
    if input_time == "-1":
        input_time = datetime.now().strftime("%H:%M:%S")

    start = int(input("Enter starting post office index: "))
    iterations = int(input("Enter the number of iterations: "))

    dis_matrices = []
    for i in range(4):
        try:
            matrix = make_matrix(f"data/post_office_with_info_{9 + i}.json")
            dis_matrices.append(matrix)
        except FileNotFoundError:
            break

    alpha_coeff = 0.5
    best_route, best_time = simulated_annealing(input_time, start, iterations, dis_matrices, alpha_coeff)

    print(f"Best Route: {best_route}")
    print(f"Best Time: {best_time}")


if __name__ == "__main__":
    main()
