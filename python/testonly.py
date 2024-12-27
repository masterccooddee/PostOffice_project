import threading
import random
import math
import time

def simulated_annealing(thread_id, initial_temperature, cooling_rate, iterations):
    # 定義目標函數（這裡假設為單峰函數）
    def objective_function(x):
        return -x**2 + 4*x

    # 初始化變量
    current_solution = random.uniform(-10, 10)
    current_value = objective_function(current_solution)
    best_solution = current_solution
    best_value = current_value

    temperature = initial_temperature
    print(f"Thread {thread_id} - Start: Initial Solution={current_solution:.2f}, Value={current_value:.2f}")

    for i in range(iterations):
        # 生成鄰近解
        new_solution = current_solution + random.uniform(-1, 1)
        new_value = objective_function(new_solution)

        # 判斷是否接受新解
        if new_value > current_value or random.uniform(0, 1) < math.exp((new_value - current_value) / temperature):
            current_solution = new_solution
            current_value = new_value

            # 更新最佳解
            if current_value > best_value:
                best_solution = current_solution
                best_value = current_value

        # 降溫
        temperature *= cooling_rate

        # 顯示進度
        if i % (iterations // 10) == 0 or i == iterations - 1:
            print(f"Thread {thread_id} - Progress: {i / iterations * 100:.2f}% | Best Value={best_value:.2f}")

    print(f"Thread {thread_id} - Finished: Best Solution={best_solution:.2f}, Best Value={best_value:.2f}")

# 設定參數
num_threads = 4
initial_temperature = 100
cooling_rate = 0.95
iterations = 1000

# 啟動多線程
threads = []
for thread_id in range(num_threads):
    thread = threading.Thread(target=simulated_annealing, args=(thread_id, initial_temperature, cooling_rate, iterations))
    threads.append(thread)
    thread.start()

# 等待所有線程完成
for thread in threads:
    thread.join()

print("所有線程完成模擬退火。")
