import threading
import colorama
from bs4 import BeautifulSoup
from utils.TimeRemaining import TimeRemaining
from utils.bdd_class import ConnectionDatabase
from utils.scrap_class import Scrap
from utils.shift_class import PressShift



def get_wiki_url(voc):
    global scrap
    global db

    soup = BeautifulSoup(scrap.get_one(), "lxml")
    wiki_url = soup.find_all("a", href=lambda href: href and href.startswith("http://ja.wikipedia.org/wiki/"))

    if wiki_url is None or len(wiki_url) == 0:
        print(colorama.Fore.RED, "Pas d'url dans cette page", colorama.Fore.RESET)
        with open("save/error.txt", "a", encoding="utf-8") as f:
            f.write(str(voc[0])+"\thttps://jisho.org/"+voc[1]+"\n")
        return

    wiki_url = wiki_url[0]['href'].replace("http://ja.wikipedia.org/", "")
    print(colorama.Fore.YELLOW, wiki_url, "\n", colorama.Fore.RESET)

    try:
        db.cursor.execute("UPDATE `voc` SET `url`=%s WHERE `id`=%s", (wiki_url, voc[0]))
        db.conn.commit()
    except Exception as e:
        print(colorama.Fore.RED, "Un problème est survenu lors de l'insertion dans la base de données :", e, colorama.Fore.RESET)
        with open("save/error.txt", "a", encoding="utf-8") as f:
            f.write(str(voc[0])+"\thttps://jisho.org/"+voc[1]+"\n")



if __name__ == "__main__":
    colorama.init()
    PressShift()
    scrap = Scrap("https://jisho.org/")

    db = ConnectionDatabase()
    db.cursor.execute("SELECT `id`,`url` FROM `voc` WHERE `url` NOT LIKE '%\%%' AND `url` NOT LIKE 'wiki%'")
    wiki = db.cursor.fetchall()

    tm = TimeRemaining(len(wiki))
    scrap.fetch_url(wiki[0][1])

    for i in range(len(wiki)):
        tm.print_time_and_percent(i)
        print(wiki[i][0])

        if i+1 >= len(wiki):
            get_wiki_url(wiki[i])
            continue
        t1 = threading.Thread(target=scrap.fetch_url, args=(wiki[i+1][1],))
        t2 = threading.Thread(target=get_wiki_url, args=(wiki[i],))
        t1.start()
        t2.start()
        t1.join()
        t2.join()
    db.close()

