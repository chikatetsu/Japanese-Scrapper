import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import threading
import urllib.parse
import multiprocessing
import time
import pyautogui as pag
import colorama


url = "https://jisho.org"
base_url = "https:"


class Observable:
    def __init__(self):
        self.observers = []
        self.url = []
        self.html = []

    def add_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self):
        for observer in self.observers:
            observer.on_append(self)

    def add_data(self, url, html):
        self.url.append(url)
        self.html.append(html)
        self.notify_observers()

    def remove_data(self, url, html):
        self.url.remove(url)
        self.html.remove(html)


class Observer:
    def on_append(self, observable):
        try:
            get_links()
            print_current_link()
            save_index()
            observable.remove_data(observable.url[0], observable.html[0])
        except Exception as e:
            print(colorama.Fore.RED, e, colorama.Style.RESET_ALL)


def move_mouse():
    while True:
        time.sleep(120)
        t = pag.position()
        pag.moveTo(1000,1, duration=0.2)
        pag.click()
        pag.moveTo(t[0], t[1], duration=0.2)


def add_links(links, newLinks):
    with open("save/allURL.txt", "a", encoding='utf-8') as f:
        for l in newLinks:
            if l not in links:
                links.append(l)
                f.write("\n"+l)
    return links


def format_links(links):
    result = []
    for l in links:
        l = l['href']

        if "?" in l:
            query_params = l.split("?")[1].split("&")
            l = l.split("?")[0]
            for param in query_params:
                if param.startswith("page="):
                    l += "?" + param
                    break
        l = l.replace("sentences", "sentence")
        l = l.replace("sentence", "sentences")

        if l.startswith('//jisho.org'):
            result.append(urljoin(base_url, l))
        elif l.startswith('/'):
            result.append(urljoin(url, l))
        elif l.startswith(url):
            result.append(l)
    return result


def save_index():
    global index
    index += 1
    with open("save/processURL.txt", "w", encoding="utf-8") as f:
        f.write(str(index))


def get_links():
    global links
    global observable
    soup = BeautifulSoup(observable.html[0], "html.parser")
    links = add_links(links, format_links(soup.find_all("a", href=True)))


def init_links():
    global links
    with open("save/allURL.txt", "r", encoding="utf-8") as f:
        links = list(map(str, f.read().split("\n")))


def init_index():
    global index
    with open("save/processURL.txt", "r", encoding="utf-8") as f:
        index = int(f.read())


def print_current_link():
    global observable
    global index
    global links
    global lenLinks
    if lenLinks < len(links):
        print(colorama.Fore.YELLOW, "{:.3f}".format((index/len(links))*100), "%\t", index, "\t", urllib.parse.unquote(observable.url[0]), colorama.Style.RESET_ALL)
    else :
        print(colorama.Fore.GREEN, "{:.3f}".format((index/len(links))*100), "%\t", index, "\t", urllib.parse.unquote(observable.url[0]), colorama.Style.RESET_ALL)
    lenLinks = len(links)


def get_url(current_index):
    global links
    global observable
    response = requests.get(links[current_index], timeout=180)
    observable.add_data(links[current_index], response.content)


if __name__ == '__main__':
    processus = multiprocessing.Process(target=move_mouse)
    processus.start()
    colorama.init()

    links = []
    index = 0
    t1 = threading.Thread(target=init_links)
    t2 = threading.Thread(target=init_index)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    lenLinks = len(links)
    i = index
    observable = Observable()
    observable.add_observer(Observer())

    while i < len(links):
        get_url(i)
        i += 1
