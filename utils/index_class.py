class Index:
    def __init__(self, filename):
        """ Needs the name of the file that will save the index """
        self.__filename = filename
        self.value = self._load()

    def _load(self):
        """ Load the index from the file """
        with open(self.__filename, "r", encoding="utf-8") as f:
            return int(f.read())

    def save(self):
        """ Save the current index value in the file """
        with open(self.__filename, "w", encoding="utf-8") as f:
            f.write(str(self.value))

    def increment(self):
        """ Increment the index value """
        self.value += 1
