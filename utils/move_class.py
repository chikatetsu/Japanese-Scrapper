import multiprocessing
import time
import pyautogui as pag


class MoveMouse:
    def __init__(self):
        """ Move the mouse every 2 minutes to avoid the computer to go to sleep """
        processus = multiprocessing.Process(target=self._move_mouse)
        processus.start()

    @staticmethod
    def _move_mouse():
        while True:
            time.sleep(120)
            t = pag.position()
            pag.moveTo(1000, 1, duration=0.2)
            pag.click()
            pag.moveTo(t[0], t[1], duration=0.2)
