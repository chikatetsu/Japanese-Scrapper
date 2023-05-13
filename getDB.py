from bs4 import BeautifulSoup
import threading
import multiprocessing
import time
import pyautogui as pag
import colorama
import requests
from ctypes import windll

from utils.bdd_class import ConnectionDatabase


def init_links():
    global links
    with open("save/phrase.txt", "r", encoding="utf-8") as f:
        links = list(map(str, f.read().split("\n")))


def init_index():
    global index
    with open("save/processDB.txt", "r", encoding="utf-8") as f:
        index = int(f.read())


def move_mouse():
    while True:
        time.sleep(120)
        t = pag.position()
        pag.moveTo(1000,1, duration=0.2)
        pag.click()
        pag.moveTo(t[0], t[1], duration=0.2)


def save_index(index):
    with open("save/processDB.txt", "w", encoding="utf-8") as f:
        f.write(str(index))


def get_info_from_url(url):
    global word
    global html

    soup = BeautifulSoup(html.pop(0), "html.parser")
    jap = soup.select_one('#page_container > div > div > article > div > div.concept_light-wrapper > div.concept_light-readings > div > span.text')
    kana = soup.select_one('#page_container > div > div > article > div > div.concept_light-wrapper > div.concept_light-readings > div > span.furigana')
    fra = soup.select_one('#page_container > div > div > article > div > div.concept_light-meanings.medium-9.columns > div > div.meaning-wrapper > div > span.meaning-meaning')
    categ = soup.select_one('#page_container > div > div > article > div > div.concept_light-meanings.medium-9.columns > div > div.meaning-tags')

    if jap is not None: jap = jap.text.strip()
    else:
        print(colorama.Fore.RED, "L'attribut jap n'a pas été trouvé pour le mot courant", colorama.Fore.RESET)
        with open("save/error.txt", "a", encoding="utf-8") as f:
            f.write("https://jisho.org/"+url+"\n")
        jap = ""
    if kana is not None: kana = kana.text.strip()
    else:
        print(colorama.Fore.RED, "L'attribut kana n'a pas été trouvé pour le mot courant", colorama.Fore.RESET)
        with open("save/error.txt", "a", encoding="utf-8") as f:
            f.write("https://jisho.org/"+url+"\n")
        kana = ""
    if fra is not None: fra = fra.text.strip()
    else:
        print(colorama.Fore.RED, "L'attribut fra n'a pas été trouvé pour le mot courant", colorama.Fore.RESET)
        with open("save/error.txt", "a", encoding="utf-8") as f:
            f.write("https://jisho.org/"+url+"\n")
        fra = ""
    if categ is not None: categ = categ.text.strip()
    else:
        print(colorama.Fore.RED, "L'attribut categ n'a pas été trouvé pour le mot courant", colorama.Fore.RESET)
        with open("save/error.txt", "a", encoding="utf-8") as f:
            f.write("https://jisho.org/"+url+"\n")
        categ = ""

    word = (jap, kana, fra, categ)
    insert_in_db(url)


def print_voc(index, end):
    global word
    jap, kana, fra, categ = word
    print(colorama.Fore.CYAN, "{:.3f}".format((index/end)*100), "%\t", index, colorama.Fore.RESET)
    print("fra=" + fra)
    print("jap=" + jap)
    if kana != "" :
        print("kana=" + kana)
    print("categories=" + categ + "\n")


def fetch_url(url):
    global html
    connected = False
    error_message_displayed = False

    while not connected:
        try:
            response = requests.get("https://jisho.org/" + url, timeout=None)
            connected = True
            html.append(response.content)

        except requests.exceptions.RequestException as e:
            if not error_message_displayed:
                print(colorama.Fore.RED, "ERREUR DE CONNEXION : Veuillez vérifier votre connexion internet", colorama.Fore.RESET)
                error_message_displayed = True
            restart_vpn()
            time.sleep(30)


def restart_vpn():
    hdc = windll.user32.GetDC(0)
    windll.user32.ScreenToClient()
    color = 0
    x = 1300
    while color != 6684927 or x > 1920:
        color = windll.gdi32.GetPixel(hdc, x, 1050)
        x += 1

    pag.moveTo(x, 1050)
    pag.click()
    time.sleep(1)
    pag.moveTo(800, 540)
    pag.click()


def insert_in_db(url):
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
            f.write("https://jisho.org/"+url+"\n")



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

    db = ConnectionDatabase()

    word = list()
    html = []
    fetch_url(links[index])

    while index < len(links):
        if index + 1 >= len(links):
            get_info_from_url(links[index])
        else:
            t1 = threading.Thread(target=fetch_url, args=(links[index+1],))
            t2 = threading.Thread(target=get_info_from_url, args=(links[index],))
            t1.start()
            t2.start()
            t1.join()
            t2.join()
        print_voc(index, len(links))
        save_index(index)
        index += 1

    db.close()
