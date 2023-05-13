from bs4 import BeautifulSoup
import threading
import colorama
from utils.TimeRemaining import TimeRemaining
from utils.bdd_class import ConnectionDatabase
from utils.index_class import Index
from utils.scrap_class import Scrap
from utils.shift_class import PressShift



def get_info_from_url(voc):
    global scrap
    global db

    soup = BeautifulSoup(scrap.get_one(), "html.parser")
    fra = soup.select_one('#page_container > div > div > article > div > div.concept_light-meanings.medium-9.columns > div > div.meaning-wrapper > div > span.meaning-meaning')

    if fra is None:
        print(colorama.Fore.RED, "L'attribut fra n'a pas été trouvé pour le mot courant", colorama.Fore.RESET)
        with open("save/error.txt", "a", encoding="utf-8") as f:
            f.write(str(voc[0])+"\thttps://jisho.org/"+voc[1]+"\n")
        return

    fra = fra.text.strip()
    print(voc[0], "\t", fra, "\n")
    try:
        db.cursor.execute("UPDATE `voc` SET `fra`=%s WHERE `id`=%s", (fra, voc[0]))
        db.conn.commit()
    except Exception as e:
        print(colorama.Fore.RED, "Un problème est survenu lors de l'insertion dans la base de données :", e, colorama.Fore.RESET)
        with open("save/error.txt", "a", encoding="utf-8") as f:
            f.write(str(voc[0])+"\thttps://jisho.org/"+voc[1]+"\n")



if __name__ == '__main__':
    colorama.init()
    PressShift()
    scrap = Scrap("https://jisho.org/")
    index = Index("save/processDB.txt")

    db = ConnectionDatabase()
    db.cursor.execute("SELECT `id`, `url` FROM `voc` WHERE (`difficulteJP`!=0 OR `difficulteJP` IS NULL) AND `id`>=%s AND `url` LIKE '%\%%' AND `url` NOT LIKE 'wiki%' ORDER BY `id` ASC", (index.value,))
    links = db.cursor.fetchall()

    tm = TimeRemaining(len(links))
    scrap.fetch_url(links[0][1])

    for i in range(len(links)):
        tm.print_time_and_percent(i)

        if i+1 >= len(links):
            get_info_from_url(links[i])
            continue
        else:
            t1 = threading.Thread(target=scrap.fetch_url, args=(links[i+1][1],))
            t2 = threading.Thread(target=get_info_from_url, args=(links[i],))
            t1.start()
            t2.start()
            t1.join()
            t2.join()
        index.value = links[i][0]
        index.save()
    db.close()
