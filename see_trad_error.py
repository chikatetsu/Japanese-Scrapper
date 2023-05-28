import time
import webbrowser
import colorama
import pyautogui as pag
from bs4 import BeautifulSoup
from utils.bdd_class import ConnectionDatabase
from utils.scrap_class import Scrap



def close_tab(nb_tabs=1):
    webbrowser.open("https://www.google.com")
    time.sleep(0.5)
    for i in range(0, nb_tabs+1):
        pag.hotkey('ctrl', 'w')
    pag.moveTo(1800, 500)
    pag.click()



def get_trad():
    global wordreference
    soup = BeautifulSoup(wordreference.get_one(), "html.parser")
    fra = soup.select('#articleWRD table.WRD tr.even td.ToWrd')

    if fra is None or len(fra) == 0:
        return ""

    return fra[0].contents[0].text.rstrip()



def remove_id_from_errors():
    id_to_remove = ids[0]
    while id_to_remove in ids:
        ids.remove(id_to_remove)

    with open("save/trad_err.txt", "w", encoding="utf-8") as f:
        f.write('\n'.join(ids))



if __name__ == '__main__':
    with open("save/trad_err.txt", "r", encoding="utf-8") as f:
        ids = f.read()
    ids = ids.split('\n')
    db = ConnectionDatabase()
    wordreference = Scrap("https://www.wordreference.com/enfr/")
    colorama.init()

    while len(ids) > 0:
        print(colorama.Fore.CYAN, "Restant :", len(ids), colorama.Fore.RESET)

        db.cursor.execute("SELECT `id`,`fra`,`jap`,`kana`,`difficulteJP`,`url` FROM `voc` WHERE `id`=%s", (ids[0],))
        voc = db.cursor.fetchone()

        if voc is None:
            remove_id_from_errors()
            continue
        if voc[4] == 0:
            print(colorama.Fore.GREEN, voc[0], voc[1], voc[2], voc[3], colorama.Fore.RESET)
            remove_id_from_errors()
            continue
        if "%" not in voc[5]:
            print(colorama.Fore.YELLOW, voc[0], voc[1], voc[2], voc[3], colorama.Fore.RESET)
            remove_id_from_errors()
            continue
        if voc[5].startswith("wiki/"):
            print(colorama.Fore.YELLOW, voc[0], voc[1], voc[2], voc[3], colorama.Fore.RESET)
            remove_id_from_errors()
            continue


        newfra = ""
        print(voc)
        tabsDisplayed = False
        for eng in voc[1].split(';'):
            trad = ""
            if newfra != "":
                newfra += ";"

            if ';' in voc[1]:
                wordreference.fetch_url(eng)
                trad = get_trad()
            if trad != "":
                newfra += trad
                continue

            webbrowser.open("https://www.google.com/search?q=" + eng)
            webbrowser.open("https://www.reverso.net/traduction-texte#sl=eng&tl=fra&text=" + eng)
            tabsDisplayed = True
            newfra += input(eng + "=") or eng
            close_tab(2)


        print(colorama.Fore.GREEN, newfra, colorama.Fore.RESET)
        db.cursor.execute("UPDATE `voc` SET `fra`=%s,`difficulteJP`=0 WHERE `id`=%s", (newfra,voc[0]))
        db.conn.commit()
        remove_id_from_errors()
        print()
