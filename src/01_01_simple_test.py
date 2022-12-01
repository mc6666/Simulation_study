# 載入套件
import simpy

# 建立一個處理作業，輸入參數為env
def clock(env):
    while True:
        print("開始：", env.now)  # env.now獲取當前時間
        yield env.timeout(1)  # 等待1秒
        print("結束：", env.now)  # env.now獲取當前時間


# 建立環境
env = simpy.Environment()
# 啟動處理作業
env.process(clock(env))
# 運行模擬環境5秒
env.run(until=5)
