import threading
import requests
from bs4 import BeautifulSoup
import colorama
from utils.bdd_class import ConnectionDatabase


def fetch_word(word):
    global html
    global yahoo
    response = requests.get(yahoo + word, timeout=180)
    html.append(response.content)


def get_difficulty_yahoo():
    global html
    global db
    soup = BeautifulSoup(html.pop(), "html.parser")
    total_res = soup.select_one("#inf")

    if total_res is None:
        print(colorama.Fore.RED, "IMPOSSIBLE DE RÉCUPÉRER L'ADRESSE :\n", colorama.Fore.RESET, soup)
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



if __name__ == '__main__':
    colorama.init()
    db = ConnectionDatabase()

    # Récupère le mot avant de le chercher
    db.cursor.execute("SELECT `id`,`jap` FROM `voc` WHERE `difficulteJP` IS NULL")
    allVoc = db.cursor.fetchall()

    db.cursor.execute("SELECT AVG(`difficulte`) FROM `voc`")
    avg = db.cursor.fetchone()[0]
    db.cursor.execute("SELECT AVG(`difficulte`) FROM `voc` WHERE `difficulte`<%s", (avg,))
    low_avg = db.cursor.fetchone()[0]
    db.cursor.execute("SELECT AVG(`difficulte`) FROM `voc` WHERE `difficulte`>%s", (avg,))
    high_avg = db.cursor.fetchone()[0]


    html = []
    yahoo = "https://search.yahoo.co.jp/search?p="
    fetch_word(allVoc[0][1])

    for i in range(len(allVoc)):
        print(allVoc[i][1])

        t1 = threading.Thread(target=fetch_word, args=(allVoc[i+1][1],))
        t2 = threading.Thread(target=get_difficulty_yahoo)
        t1.start()
        t2.start()
        t1.join()
        t2.join()

    # Fermer la connexion
    db.close()
