import time
import urllib
from urllib.parse import urljoin, urlparse
import threading
import colorama
from bs4 import BeautifulSoup

from utils.time_remaining import TimeRemaining
from utils.index_class import Index
from utils.links_class import Links
from utils.scrap_class import Scrap
from utils.shift_class import PressShift


def get_links():
    global links
    global scrap
    soup = BeautifulSoup(scrap.get_one(), "html.parser")
    links.add_links(format_links(soup.find_all("a", href=True)))


def get_website_name(url):
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}"


def format_links(urls):
    result = []
    for l in urls:
        l = l['href']
        l = l.replace(scrap.base_url, '')
        l = l.replace('//www3.nhk.or.jp', '')

        if l.startswith('http:/news'):
            l = l.replace('http:', '')

        if not l.startswith('/'):
            if not l.startswith('http'):
                continue
            known_links.add_links([get_website_name(l)])
            continue
        result.append(l)
    return result



def print_current_link():
    global index
    global links
    if links.were_added:
        print(colorama.Fore.YELLOW,
              "{:.3f}".format((index.value/len(links))*100),
              f"%\t{index.value}\t{urllib.parse.unquote(links.get_value(index.value))}",
              colorama.Fore.RESET)
    else :
        print(colorama.Fore.GREEN,
              "{:.3f}".format((index.value/len(links))*100),
              f"%\t{index.value}\t{urllib.parse.unquote(links.get_value(index.value))}",
              colorama.Fore.RESET)



if __name__ == '__main__':
    PressShift()
    colorama.init()
    scrap = Scrap("https://www3.nhk.or.jp")
    index = Index("save/nhk3_index.txt")
    links = Links("save/nhk3.txt")
    tm = TimeRemaining(len(links))
    scrap.fetch_url(links.get_value(index.value))
    known_links = Links("save/known_links.txt")

    while index.value < len(links):
        try:
            if index.value + 1 >= len(links):
                get_links()
            else:
                t1 = threading.Thread(target=get_links)
                t2 = threading.Thread(target=scrap.fetch_url, args=(links.get_value(index.value + 1),))
                t1.start()
                t2.start()
                t1.join()
                t2.join()

            index.increment()
            index.save()
            if index.value % 50 == 0:
                tm.length = len(links)
                tm.print_time_and_percent(index.value)
            print_current_link()
        except Exception as e:
            print(colorama.Fore.RED, f"Erreur de connexion pour l'url {links.get_value(index.value)} à l'index {index.value}\n{e}", colorama.Fore.RESET)
            time.sleep(10)
