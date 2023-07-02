import os
import time
from bs4 import BeautifulSoup
import colorama
from utils.bdd_class import ConnectionDatabase
from utils.scrap_class import Scrap



def get_difficulty_yahoo():
    global scrap
    global db
    soup = BeautifulSoup(scrap.get_one(), "html.parser")
    total_res = soup.select_one("#inf")

    if total_res is None:
        print(colorama.Fore.RED, "IMPOSSIBLE DE RÉCUPÉRER L'ADRESSE\n", colorama.Fore.RESET)
        with open("save/err.html", "w", encoding="utf-8") as f:
            f.write(str(soup))
        get_new_proxy()
        return

    total_res = total_res.text.strip()
    debut = total_res.find("件目 / 約") + len("件目 / 約")
    fin = total_res.find("件 - ", debut)
    total_res = total_res[debut:fin]
    total_res = int(total_res.replace(',', ''))
    print_res(total_res)
    db.cursor.execute("UPDATE `voc` SET `difficulteJP`=%s WHERE `id`=%s", (total_res, allVoc[i][0]))
    db.conn.commit()


def print_res(total):
    global avg
    global low_avg
    global high_avg

    if total < low_avg:
        print(colorama.Fore.MAGENTA, total, "\n", colorama.Fore.RESET)
        return
    if total < avg:
        print(colorama.Fore.RED, total, "\n", colorama.Fore.RESET)
        return
    if total < high_avg:
        print(colorama.Fore.YELLOW, total, "\n", colorama.Fore.RESET)
        return
    print(colorama.Fore.GREEN, total, "\n", colorama.Fore.RESET)


def get_new_proxy():
    with open("http_proxies.txt", "r", encoding="utf-8") as f:
        lines = f.read().split("\n")
    if len(lines) == 0:
        print(colorama.Fore.RED, "NO PROXIE IN THE FILE. PLEASE RESTART WITH NEW PROXIES", colorama.Fore.RESET)
        while True:
            time.sleep(10)
    print(colorama.Fore.MAGENTA, f"NEW PROXY CONNECTION :", lines[0], colorama.Fore.RESET)
    if lines[0].startswith("http://"):
        os.environ['http_proxy'] = lines[0]
    else:
        os.environ['https_proxy'] = lines[0]

    with open("http_proxies.txt", "w", encoding="utf-8") as f:
        for l in lines[1:]:
            f.write(l + "\n")
    with open("http_proxies.txt", "a", encoding="utf-8") as f:
        f.write(lines[0])



if __name__ == '__main__':
    colorama.init()
    get_new_proxy()
    scrap = Scrap("https://search.yahoo.co.jp/search?p=")
    db = ConnectionDatabase()

    # Récupère le mot avant de le chercher
    db.cursor.execute("SELECT `id`,`jap` FROM `voc` WHERE `difficulteJP`=0")
    allVoc = db.cursor.fetchall()

    db.cursor.execute("SELECT AVG(`difficulteJP`) FROM `voc`")
    avg = db.cursor.fetchone()[0]
    db.cursor.execute("SELECT AVG(`difficulteJP`) FROM `voc` WHERE `difficulteJP`<%s", (avg,))
    low_avg = db.cursor.fetchone()[0]
    db.cursor.execute("SELECT AVG(`difficulteJP`) FROM `voc` WHERE `difficulteJP`>%s", (avg,))
    high_avg = db.cursor.fetchone()[0]

    for i in range(len(allVoc)):
        print(allVoc[i][1])
        scrap.fetch_url(allVoc[i][1])
        get_difficulty_yahoo()

    db.close()
