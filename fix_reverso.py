from bs4 import BeautifulSoup
import threading
import time
import colorama
from utils.time_remaining import TimeRemaining
from utils.bdd_class import ConnectionDatabase
from utils.scrap_class import Scrap


def get_eng_trad(word):
    """ Get the english traduction of the word """
    global db
    global scrap

    soup = BeautifulSoup(scrap.get_one(), "html.parser")
    fra = soup.select_one('#page_container > div > div > article > div > div.concept_light-meanings.medium-9.columns > div > div.meaning-wrapper > div > span.meaning-meaning')

    if fra is None:
        print(colorama.Fore.RED, "L'attribut fra n'a pas été trouvé pour le mot courant", colorama.Fore.RESET)
        with open("save/error.txt", "a", encoding="utf-8") as f:
            f.write("https://jisho.org/" + word[1] + "\n")
        return

    fra = fra.text.strip()
    print(fra + "\n")

    try:
        db.cursor.execute("UPDATE `voc` SET `fra`=%s WHERE `id`=%s", (fra, word[0]))
        db.conn.commit()

    except Exception as e:
        print(colorama.Fore.RED, "Un problème est survenu lors de l'insertion dans la base de données :", e,
              colorama.Style.RESET_ALL)
        with open("save/error.txt", "a", encoding="utf-8") as f:
            f.write("https://jisho.org/" + word[1] + "\n")
        while True:
            time.sleep(10)



if __name__ == '__main__':
    colorama.init()
    scrap = Scrap("https://jisho.org/")
    db = ConnectionDatabase()

    # Get all the url of the words that need to be fixed
    db.cursor.execute("SELECT `id`,`url` FROM `voc` WHERE `fra`=''")
    url = db.cursor.fetchall()

    tm = TimeRemaining(len(url))
    scrap.fetch_url(url[0][1])

    for i in range(len(url)):
        tm.print_percent(i)
        if i+1 >= len(url):
            get_eng_trad(url[i][1])
            continue
        t1 = threading.Thread(target=scrap.fetch_url, args=(url[i+1][1],))
        t2 = threading.Thread(target=get_eng_trad, args=(url[i],))
        t1.start()
        t2.start()
        t1.join()
        t2.join()

    db.close()
