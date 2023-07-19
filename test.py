import time
for i in range(5):
    time.sleep(0.5)
    print(f"{i}/5", end="\r")