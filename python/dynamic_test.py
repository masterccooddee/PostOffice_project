def calculate_time_cost_matrix(route_matrix, gm_data_cache, start_time):
    """
    Use preloaded data and matrix to calculate the time cost of a route.
    """
    total_cost_time = 0
    now = start_time

    print(f"Starting calculation with route_matrix: {route_matrix}")
    for i in range(len(route_matrix) - 1):
        try:
            from_index = route_matrix[i].index(1)
            to_index = route_matrix[i + 1].index(1)
            current_pfs = gm_data_cache[now.hour]  # Get data for the current hour from cache
            travel_data = current_pfs[from_index].info.get(str(to_index))

            if not travel_data:
                print(f"Missing travel data for route: {from_index} -> {to_index}")
                continue

            travel_distance, travel_time = travel_data
            print(f"Route {from_index} -> {to_index}: travel_time = {travel_time}")

            total_cost_time += travel_time
            now += timedelta(seconds=travel_time + STAY_TIME)

        except Exception as e:
            print(f"Error calculating cost for route {i}: {e}")

    print(f"Total cost time: {total_cost_time}")
    return total_cost_time

if __name__ == "__main__":
    print("Testing calculate_time_cost_matrix")

    # Load preloaded data
    test_time = "10:00:00"
    pfs_v = preload_data(test_time)

    # Define a simple route matrix for testing
    test_route_matrix = [
        [1, 0, 0, 0],  # Start at index 0
        [0, 1, 0, 0],  # Visit index 1
        [0, 0, 1, 0],  # Visit index 2
        [0, 0, 0, 1],  # Visit index 3
        [1, 0, 0, 0],  # Return to index 0
    ]

    # Test calculate_time_cost_matrix
    start_time = get_time(test_time)
    calculate_time_cost_matrix(test_route_matrix, pfs_v, start_time)
