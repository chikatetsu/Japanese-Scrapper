import multiprocessing
import time
import pyautogui as pag


class PressShift:
    def __init__(self):
        processus = multiprocessing.Process(target=self._press_shift)
        processus.start()

    @staticmethod
    def _press_shift():
        while True:
            time.sleep(120)
            pag.press("shift")
            pag.press("ctrl")
