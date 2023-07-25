from bs4 import BeautifulSoup
import threading
import colorama
from utils.time_remaining import TimeRemaining
from utils.bdd_class import ConnectionDatabase
from utils.index_class import Index
from utils.scrap_class import Scrap
from utils.shift_class import PressShift



def init_links():
    """ Get all the links from the file """
    with open("save/phrase.txt", "r", encoding="utf-8") as f:
        return list(map(str, f.read().split("\n")))


def get_word_from_url(url):
    """ Get the word from the url """
    global word
    global scrap

    soup = BeautifulSoup(scrap.get_one(), "html.parser")
    jap = soup.select_one('#page_container > div > div > article > div > div.concept_light-wrapper > div.concept_light-readings > div > span.text')
    kana = soup.select_one('#page_container > div > div > article > div > div.concept_light-wrapper > div.concept_light-readings > div > span.furigana')
    fra = soup.select_one('#page_container > div > div > article > div > div.concept_light-meanings.medium-9.columns > div > div.meaning-wrapper > div > span.meaning-meaning')
    categ = soup.select_one('#page_container > div > div > article > div > div.concept_light-meanings.medium-9.columns > div > div.meaning-tags')

    verify_element(jap, "jap", url)
    verify_element(kana, "kana", url)
    verify_element(fra, "fra", url)
    verify_element(categ, "categ", url)

    word = (jap, kana, fra, categ)
    insert_in_db(url)



def verify_element(element, name, url):
    """ Verify if the element was found """
    if element is not None:
        return element.text.strip()
    print(colorama.Fore.RED, "L'attribut" + name + "n'a pas été trouvé pour le mot courant", colorama.Fore.RESET)
    with open("save/error.txt", "a", encoding="utf-8") as f:
        f.write(scrap.base_url+url+"\n")
    return ""


def print_voc(voc):
    """ Print the values of the word """
    jap, kana, fra, categ = voc
    print("fra=" + fra)
    print("jap=" + jap)
    if kana != "" :
        print("kana=" + kana)
    print("categories=" + categ + "\n")



def insert_in_db(url):
    """ Insert the word in the database """
    global word
    global db
    jap, kana, fra, categ = word
    categ = categ.split(", ")
    try:
        db.cursor.execute("SELECT 1 FROM `voc` WHERE `fra`=%s AND `jap`=%s", (fra, jap))
        result = db.cursor.fetchone()
        if result is not None:
            print(colorama.Fore.YELLOW, "Existe déjà, pas ajouté", colorama.Fore.RESET)
            return

        if kana != "":
            db.cursor.execute("INSERT INTO `voc` (`fra`,`jap`,`kana`,`url`) VALUES (%s,%s,%s,%s)", (fra, jap, kana, url))
        else:
            db.cursor.execute("INSERT INTO `voc` (`fra`,`jap`,`url`) VALUES (%s,%s,%s)", (fra, jap, url))
        for c in categ:
            db.cursor.execute(
                "INSERT INTO `categorie` (`nom`) SELECT %s WHERE NOT EXISTS(SELECT 1 FROM `categorie` WHERE `nom` = %s)",(c, c))
        db.conn.commit()

        db.cursor.execute("SELECT `id` FROM `voc` WHERE `fra`=%s AND `jap`=%s", (fra, jap))
        idVoc = db.cursor.fetchone()[0]

        idCategorie = []
        for c in categ:
            db.cursor.execute("SELECT `id` FROM `categorie` WHERE `nom`=%s", [c])
            res = db.cursor.fetchone()
            if res is not None and res[0] not in idCategorie:
                idCategorie.append(res[0])

        for c in idCategorie:
            db.cursor.execute("INSERT INTO `categoriesVoc` (`idCategorie`,`idVoc`) VALUES (%s,%s)", (c, idVoc))
        db.conn.commit()
        print(colorama.Fore.GREEN, "Ajouté à la bdd", colorama.Fore.RESET)

    except Exception as e:
        print(colorama.Fore.RED, "Un problème est survenu lors de l'insertion dans la base de données :", e, colorama.Style.RESET_ALL)
        with open("save/error.txt", "a", encoding="utf-8") as f:
            f.write(scrap.base_url+url+"\n")



if __name__ == '__main__':
    PressShift()
    colorama.init()
    links = init_links()
    index = Index("save/processDB.txt")
    scrap = Scrap("https://jisho.org/")
    tm = TimeRemaining(len(links))
    db = ConnectionDatabase()

    word = list()
    scrap.fetch_url(links[index.value])

    while index.value < len(links):
        if index.value + 1 >= len(links):
            get_word_from_url(links[index.value])
        else:
            t1 = threading.Thread(target=scrap.fetch_url, args=(links[index.value+1],))
            t2 = threading.Thread(target=get_word_from_url, args=(links[index.value],))
            t1.start()
            t2.start()
            t1.join()
            t2.join()
        tm.print_percent(index.value)
        print_voc(word)
        index.increment()
        index.save()

    db.close()
