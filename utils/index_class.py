class Index:
    def __init__(self, filename):
        self.__filename = filename
        self.value = self._load()

    def _load(self):
        with open(self.__filename, "r", encoding="utf-8") as f:
            return int(f.read())

    def save(self):
        with open(self.__filename, "w", encoding="utf-8") as f:
            f.write(str(self.value))

    def increment(self):
        self.value += 1
