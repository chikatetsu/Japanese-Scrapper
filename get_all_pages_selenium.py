import time
import urllib
from urllib.parse import urljoin, urlparse
import colorama
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import FirefoxOptions

from utils.time_remaining import TimeRemaining
from utils.index_class import Index
from utils.links_class import Links
from utils.shift_class import PressShift



def get_links(url):
    global driver
    driver.get(base_url + url)
    a_tags_with_href = driver.find_elements(By.CSS_SELECTOR, "a[href]")
    links.add_links(format_links(a_tags_with_href))


def get_website_name(url):
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}"


def format_links(urls):
    global base_url
    result = []
    for element in urls:
        l = element.get_attribute('href')
        if not l:
            continue
        l = str(l)
        if l.startswith('javascript:'):
            continue
        l = l.split('#')[0]
        l = l.replace(base_url, '')

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
    base_url = "https://www.nhk.or.jp"
    opts = FirefoxOptions()
    opts.add_argument("--headless")
    driver = webdriver.Firefox(options=opts)
    index = Index("save/nhk_index.txt")
    links = Links("save/nhk.txt")
    tm = TimeRemaining(len(links))
    known_links = Links("save/known_links.txt")

    while index.value < len(links):
        try:
            get_links(links.get_value(index.value))
            index.increment()
            index.save()
            if index.value % 50 == 0:
                tm.length = len(links)
                tm.print_time_and_percent(index.value)
            print_current_link()
        except Exception as e:
            print(colorama.Fore.RED, f"Erreur de connexion pour l'url {links.get_value(index.value)} à l'index {index.value}\n{e}", colorama.Fore.RESET)
            time.sleep(10)
    driver.quit()