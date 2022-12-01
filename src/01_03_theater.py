"""Companion code to https://realpython.com/simulation-with-simpy/

'Simulating Real-World Processes With SimPy'

Python version: 3.7.3
SimPy version: 3.0.11
"""

# 載入套件
import simpy
import random
import statistics

wait_times = [] # 記錄觀眾等待時間

# 戲院類別
class Theater(object):
    def __init__(self, env, num_cashiers, num_servers, num_ushers):
        self.env = env
        self.cashier = simpy.Resource(env, num_cashiers) # 售票口
        self.server = simpy.Resource(env, num_servers)   # 驗票口
        self.usher = simpy.Resource(env, num_ushers)     # 小吃部銷售員

    # 購票時間 1~3分鐘
    def purchase_ticket(self, moviegoer):
        yield self.env.timeout(random.randint(1, 3))

    # 驗票時間 3秒鐘
    def check_ticket(self, moviegoer):
        yield self.env.timeout(3 / 60)

    # 購物時間 1~5分鐘
    def sell_food(self, moviegoer):
        yield self.env.timeout(random.randint(1, 5))

# 觀眾進場
def go_to_movies(env, moviegoer, theater):
    # 到場
    arrival_time = env.now

    # 購票
    with theater.cashier.request() as request:
        yield request
        yield env.process(theater.purchase_ticket(moviegoer))

    # 驗票
    with theater.usher.request() as request:
        yield request
        yield env.process(theater.check_ticket(moviegoer))

    # 購物：1/2機率會購物
    if random.choice([True, False]):
        with theater.server.request() as request:
            yield request
            yield env.process(theater.sell_food(moviegoer))

    # 入座
    wait_times.append(env.now - arrival_time)


# 模擬函數
def run_theater(env, num_cashiers, num_servers, num_ushers):
    # 建立環境
    theater = Theater(env, num_cashiers, num_servers, num_ushers)

    # 建立處理作業
    for moviegoer in range(3):
        env.process(go_to_movies(env, moviegoer, theater))

    # 模擬
    while True:
        yield env.timeout(0.20)  # 每隔0.2分鐘有一觀眾到場

        moviegoer += 1
        env.process(go_to_movies(env, moviegoer, theater))


# 統計等待時間
def get_average_wait_time(wait_times):
    average_wait = statistics.mean(wait_times)
    # 計算分、秒
    minutes, frac_minutes = divmod(average_wait, 1)
    seconds = frac_minutes * 60
    return round(minutes), round(seconds)

# 設定資源個數
def get_user_input():
    # 輸入資源個數
    num_cashiers = input("售票口個數: ")
    num_servers = input("驗票口個數: ")
    num_ushers = input("小吃部銷售員人數: ")
    params = [num_cashiers, num_servers, num_ushers]
    if all(str(i).isdigit() for i in params):  # Check input is valid
        params = [int(x) for x in params]
    else:
        print(
            "Could not parse input. Simulation will use default values:",
            "\n1 cashier, 1 server, 1 usher.",
        )
        params = [1, 1, 1]
    return params


def main():
    # Setup
    random.seed(42)
    num_cashiers, num_servers, num_ushers = get_user_input()

    # 啟動模擬
    env = simpy.Environment()
    env.process(run_theater(env, num_cashiers, num_servers, num_ushers))
    env.run(until=90) # 模擬90分鐘

    # 統計等待時間
    mins, secs = get_average_wait_time(wait_times)
    print(
        "Running simulation...",
        f"\n觀眾平均進場時間：{mins} 分 {secs} 秒.",
    )


if __name__ == "__main__":
    main()
