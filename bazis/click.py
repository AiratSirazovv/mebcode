import time
import pyautogui
import pyperclip

def click(coords): 
    pyautogui.click(
        x=coords["x"], 
        y=coords["y"]
    )

    time.sleep(1)

def ctrlV(text: str):
    pyperclip.copy(text)
    time.sleep(0.1)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.1)
    pyperclip.copy('')

    time.sleep(1)

def enter():
    pyautogui.press('enter')

    time.sleep(1)