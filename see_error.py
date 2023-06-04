import time
import urllib.parse
import webbrowser
import colorama
import pyautogui as pag
from utils.bdd_class import ConnectionDatabase



def stand_url(url):
    url = urllib.parse.quote(url)
    if "wiki" in url:
        return "wiki/" + url.split("wiki/")[1]
    if "word" in url:
        return "word/" + url.split("word/")[1]


def remove_url_from_errors():
    global links
    url_to_remove = links[0]
    while url_to_remove in links:
        links.remove(url_to_remove)

    with open("save/error.txt", "w", encoding="utf-8") as f:
        f.write('\n'.join(links))


def close_tab(nb_tabs=1):
    webbrowser.open("https://www.google.com")
    time.sleep(0.5)
    for i in range(0, nb_tabs+1):
        pag.hotkey('ctrl', 'w')
    pag.moveTo(1800, 500)
    pag.click()



if __name__ == "__main__":
    with open("save/error.txt", "r", encoding="utf-8") as f:
        links = f.read()
    links = links.split('\n')
    db = ConnectionDatabase()
    colorama.init()

    for link in links:
        print(colorama.Fore.CYAN, "Restant :", len(links), colorama.Fore.RESET)
        db.cursor.execute("SELECT `id`,`fra`,`jap`,`kana`,`difficulteJP` FROM `voc` WHERE `url`=%s", (link,))
        voc = db.cursor.fetchone()

        if voc is None:
            print(colorama.Fore.RED, "url not found in the database", colorama.Fore.RESET)
            remove_url_from_errors()
            continue
        if voc[4] == 0:
            print(colorama.Fore.GREEN, voc[0], voc[1], voc[2], voc[3], colorama.Fore.RESET)
            remove_url_from_errors()
            continue

        print(voc)
        webbrowser.open("https://ja.wikipedia.org/wiki/" + voc[2])
        newfra = input(voc[1] + "=") or voc[1]
        newurl = input("url=") or link
        newurl = stand_url(newurl)
        close_tab(1)
        db.cursor.execute("UPDATE `voc` SET `fra`=%s,`url`=%s,`difficulteJP`=0 WHERE `id`=%s", (newfra, newurl, voc[0]))
        db.conn.commit()
        remove_url_from_errors()
        print()
