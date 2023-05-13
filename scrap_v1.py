import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import threading
import urllib.parse
import time
import colorama
from utils.index_class import Index
from utils.scrap_class import Scrap
from utils.shift_class import PressShift



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
            result.append(urljoin("https:", l))
        elif l.startswith('/'):
            result.append(urljoin(scrap.base_url, l))
        elif l.startswith(scrap.base_url):
            result.append(l)
    return result


def get_links():
    global links
    global scrap
    response = requests.get(scrap.get_one(), timeout=180)
    soup = BeautifulSoup(response.content, "html.parser")
    links = add_links(links, format_links(soup.find_all("a", href=True)))


def init_links():
    global links
    with open("save/allURL.txt", "r", encoding="utf-8") as f:
        links = list(map(str, f.read().split("\n")))


def print_current_link():
    global index
    global links
    global lenLinks
    if lenLinks < len(links):
        print(colorama.Fore.YELLOW, "{:.3f}".format((index.value/len(links))*100), "%\t", index, "\t", urllib.parse.unquote(links[index.value]), colorama.Fore.RESET)
    else :
        print(colorama.Fore.GREEN, "{:.3f}".format((index.value/len(links))*100), "%\t", index, "\t", urllib.parse.unquote(links[index.value]), colorama.Fore.RESET)
    lenLinks = len(links)


if __name__ == '__main__':
    PressShift()
    colorama.init()
    scrap = Scrap("https://jisho.org")
    index = Index("save/processURL.txt")
    links = []
    init_links()
    lenLinks = len(links)

    cmpt = 0
    html = []
    scrap.fetch_url(links[index.value])
    start = time.time()
    old_len = len(links)


    while index.value < len(links):
        print_current_link()
        try:
            if index.value + 1 >= len(links):
                get_links()
            else:
                t1 = threading.Thread(target=get_links)
                t2 = threading.Thread(target=scrap.fetch_url, args=(links[index.value + 1],))
                t1.start()
                t2.start()
                t1.join()
                t2.join()

            index.increment()
            index.save()
            cmpt += 1
            if cmpt % 100 == 0:
                print(colorama.Fore.CYAN, "Reste", round(
                    (((len(links) - index.value) / 100) * (time.time() - start) * ((len(links) - old_len + 100) / 100)) / 60),
                      "minutes et", len(links) - index.value, "url à traiter", colorama.Fore.RESET)
                start = time.time()
                old_len = len(links)
        except:
            print(colorama.Fore.RED, "Erreur de connexion pour l'url", links[index.value], "à l'index", index, colorama.Fore.RESET)
