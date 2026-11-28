import time
import pyautogui
from PIL import Image

OFFSET = 4

def is_ok(avg: tuple, reg: tuple, idx: int) -> bool:
    min = reg[idx] - OFFSET
    max = reg[idx] + OFFSET

    return min <= avg[idx] <= max

def _should_stop(region: tuple, reg_traget: tuple):
    screenshot = pyautogui.screenshot(region=region)
    avg = screenshot.resize((1, 1)).getpixel((0, 0))

    print(avg)

    v1 = is_ok(avg, reg_traget, 0)
    v2 = is_ok(avg, reg_traget, 1)
    v3 = is_ok(avg, reg_traget, 2)
    
    return v1 and v2 and v3

def wait_until(region: tuple, reg_traget: tuple):
    while True:
        should_stop = _should_stop(region, reg_traget)

        print(should_stop)

        if should_stop:
            break

        time.sleep(0.5)

    time.sleep(4)

def wait_until_not(region: tuple, reg_traget: tuple):
    while True:
        should_stop = not _should_stop(region, reg_traget)

        print(should_stop)

        if should_stop:
            break

        time.sleep(0.5)

    time.sleep(4)

def create_screenshot(region: tuple):
    screenshot = pyautogui.screenshot(region=region)
    screenshot.save("my_region.png")

    img = Image.open("my_region.png").convert("RGB")
    avg = img.resize((1, 1)).getpixel((0, 0))
    print(avg)
    exit()