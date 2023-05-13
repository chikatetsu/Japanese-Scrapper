import time
import colorama


class TimeRemaining:
    def __init__(self, length):
        colorama.init()
        self.length = length
        self._avr_time = 0
        self._start = time.time()

    def print_time(self, current_index, nb_iteration=1):
        self._avr_time = (self._avr_time + time.time() - self._start) / (1 + nb_iteration)
        print(colorama.Fore.CYAN, "Reste", round((self._avr_time * (self.length - current_index)) / 60), "minutes", colorama.Fore.RESET)
        self._start = time.time()

    def print_percent(self, current_index):
        print(colorama.Fore.CYAN, "{:.3f}".format((current_index / self.length) * 100), "%\t", current_index, colorama.Fore.RESET)

    def print_time_and_percent(self, current_index):
        self.print_time(current_index)
        self.print_percent(current_index)
