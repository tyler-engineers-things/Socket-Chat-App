import threading
import time



def other_thread():
    while True:
        print("Hello")
        time.sleep(1)


if __name__ == "__main__":
    other = threading.Thread(target=other_thread, name="other")
    other.start()
    for i in range (50):
        lol = input("Give input: ")