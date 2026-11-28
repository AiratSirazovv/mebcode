import pyautogui
import time

print("Push Ctrl-C for exit.")
try:
    while True:
        x, y = pyautogui.position()
        print(f"Cursor coordinates: ({x}, {y})", end="\r")
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\nExit.")