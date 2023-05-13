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


def save_index(index):
    with open("save/processURL.txt", "w", encoding="utf-8") as f:
        f.write(str(index))


def get_links():
    global links
    global link
    response = requests.get(link, timeout=180)
    soup = BeautifulSoup(response.content, "html.parser")
    links = add_links(links, format_links(soup.find_all("a", href=True)))
# def get_links():
#     global links
#     global html
#     soup = BeautifulSoup(html[0], "html.parser")
#     links = add_links(links, format_links(soup.find_all("a", href=True)))
#     html.remove(html[0])

def fetch_url(url):
    global html
    response = requests.get(url, timeout=180)
    html.append(response.content)


def init_links():
    global links
    with open("save/allURL.txt", "r", encoding="utf-8") as f:
        links = list(map(str, f.read().split("\n")))


def init_index():
    global index
    with open("save/processURL.txt", "r", encoding="utf-8") as f:
        index = int(f.read())


def print_current_link():
    global index
    global links
    global lenLinks
    if lenLinks < len(links):
        print(colorama.Fore.YELLOW, "{:.3f}".format((index/len(links))*100), "%\t", index, "\t", urllib.parse.unquote(links[index]), colorama.Fore.RESET)
    else :
        print(colorama.Fore.GREEN, "{:.3f}".format((index/len(links))*100), "%\t", index, "\t", urllib.parse.unquote(links[index]), colorama.Fore.RESET)
    lenLinks = len(links)


if __name__ == '__main__':
    processus = multiprocessing.Process(target=move_mouse)
    processus.start()
    colorama.init()

    links = []
    index = 0
    init_links()
    init_index()
    lenLinks = len(links)

    cmpt = 0
    html = []
    fetch_url(links[index])
    start = time.time()
    old_len = len(links)


    while index < len(links):
        print_current_link()
        try:
            if index + 1 >= len(links):
                get_links()
            else:
                t1 = threading.Thread(target=get_links)
                t2 = threading.Thread(target=fetch_url, args=(links[index + 1],))
                t1.start()
                t2.start()
                t1.join()
                t2.join()

            index += 1
            save_index(index)
            cmpt += 1
            if cmpt % 100 == 0:
                print(colorama.Fore.CYAN, "Reste", round(
                    (((len(links) - index) / 100) * (time.time() - start) * ((len(links) - old_len + 100) / 100)) / 60),
                      "minutes et", len(links) - index, "url à traiter", colorama.Fore.RESET)
                start = time.time()
                old_len = len(links)
        except:
            print(colorama.Fore.RED, "Erreur de connexion pour l'url", links[index], "à l'index", index, colorama.Fore.RESET)

