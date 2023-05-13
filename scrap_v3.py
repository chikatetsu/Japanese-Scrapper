import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import threading
import urllib.parse
import multiprocessing
import time
import pyautogui as pag
import colorama
import concurrent.futures


url = "https://jisho.org"
base_url = "https:"


def init_links():
    global links
    with open("save/allURL.txt", "r", encoding="utf-8") as f:
        links = list(map(str, f.read().split("\n")))


def init_index():
    global index
    with open("save/processURL.txt", "r", encoding="utf-8") as f:
        index = int(f.read())


def move_mouse():
    while True:
        time.sleep(120)
        t = pag.position()
        pag.moveTo(1000, 1, duration=0.2)
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


def get_links(html):
    global links
    soup = BeautifulSoup(html, "html.parser")
    links = add_links(links, format_links(soup.find_all("a", href=True)))


def print_current_link(url):
    global index
    global links
    global lenLinks
    if lenLinks < len(links):
        print(colorama.Fore.YELLOW, "{:.3f}".format((index/len(links))*100), "%\t", index, "\t", urllib.parse.unquote(url), colorama.Fore.RESET)
    else :
        print(colorama.Fore.GREEN, "{:.3f}".format((index/len(links))*100), "%\t", index, "\t", urllib.parse.unquote(url), colorama.Fore.RESET)
    lenLinks = len(links)


def fetch_url(url):
    response = requests.get(url, timeout=180)
    return (url, response.content)


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

    while index < len(links):
        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            i = index
            futures = []
            cmpt = 0
            start = time.time()
            old_len = len(links)

            while i < len(links) :
                try:
                    futures.append(executor.submit(fetch_url, links[i]))
                    i += 1
                except:
                    print(colorama.Fore.RED, "Timeout for url", links[i], "at index", i, colorama.Fore.RESET)

            for future in concurrent.futures.as_completed(futures):
                url, content = future.result()
                get_links(content)
                print_current_link(url)
                save_index()
                cmpt += 1
                if cmpt % 100 == 0:
                    print(colorama.Fore.CYAN, "Reste", round((((len(links)-index)/100) * (time.time()-start) * ((len(links)-old_len+100)/100))/60), "minutes et", i-index, "url à traiter", colorama.Fore.RESET)
                    start = time.time()
                    old_len = len(links)
                futures.remove(future)

            executor.shutdown(wait=False)
