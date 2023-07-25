import os


class Links:
    def __init__(self, filename):
        """ Needs the name of the file where links will be saved """
        self.__filename = filename
        self.value = self._load()
        self.were_added = False

    def _load(self):
        """ Load all saved links from the file. If the file doesn't exist, it's created with the first url """
        if not os.path.exists(self.__filename):
            with open(self.__filename, "w", encoding="utf-8") as f:
                f.write("/")
            return ["/"]
        with open(self.__filename, "r", encoding="utf-8") as f:
           return list(map(str, f.read().split("\n")))

    def add_links(self, newLinks):
        """ Add new links and save it in the file """
        self.were_added = False
        with open(self.__filename, "a", encoding='utf-8') as f:
            for l in newLinks:
                if l not in self.value:
                    self.value.append(l)
                    f.write("\n" + str(l))
                    self.were_added = True

    def get_value(self, index):
        """ Get the url at the index 'index' """
        return self.value[index]
    def __len__(self):
        """ Returns the number of links """
        return len(self.value)
