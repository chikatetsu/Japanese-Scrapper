import time
import colorama


class TimeRemaining:
    def __init__(self, length):
        """ Needs the total number of iterations """
        colorama.init()
        self.length = length
        self._avr_time = 0
        self._start = time.time()



    def print_time(self, current_index, nb_iteration=1):
        """ Print the remaining time

         :param current_index: The current iteration
         :param nb_iteration: The number of iteration that has been done since the last call of this function"""
        self._avr_time = (self._avr_time + time.time() - self._start) / (1 + nb_iteration)
        minutes = int((self._avr_time * (self.length - current_index)) / 60)
        hours = int(minutes / 60)
        days = int(hours / 24)

        print(colorama.Fore.CYAN, "Reste", end=" ")
        if days > 0:
            print(str(days) + "j", end=" ")
        if hours > 0:
            print(str(hours % 24) + "h", end=" ")
        print(str(minutes % 60) + "min", colorama.Fore.RESET)
        self._start = time.time()



    def print_percent(self, current_index):
        """ Print the percentage of the progression

        :param current_index: The current iteration"""
        print(colorama.Fore.CYAN, "{:.3f}".format((current_index / self.length) * 100), "%\t", current_index, colorama.Fore.RESET)



    def print_time_and_percent(self, current_index):
        """ Print the remaining time and the percentage of the progression

        :param current_index: The current iteration"""
        self.print_time(current_index)
        self.print_percent(current_index)
