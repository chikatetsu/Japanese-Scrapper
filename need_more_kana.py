import multiprocessing
import threading
import colorama
import regex as re
from bs4 import BeautifulSoup
import requests
import time
import pyautogui as pag

from utils.bdd_class import ConnectionDatabase


def save_index(index):
    with open("save/processNMK.txt", "w", encoding="utf-8") as f:
        f.write(str(index))

def init_index():
    global index
    with open("save/processNMK.txt", "r", encoding="utf-8") as f:
        index = int(f.read())

def move_mouse():
    while True:
        time.sleep(120)
        t = pag.position()
        pag.moveTo(1000,1, duration=0.2)
        pag.click()
        pag.moveTo(t[0], t[1], duration=0.2)


def is_japanese_word(word):
    """
    Vérifie si un mot contient des caractères japonais écrits avec un mélange de kanji et de kana.
    Retourne True si le mot contient des kanji et des kana, sinon False.
    """
    kanji_pattern = re.compile(r'[\p{Han}\p{Common}]+')
    kana_pattern = re.compile(r'[\p{Hiragana}\p{Katakana}ー]+')
    has_kanji = kanji_pattern.search(word)
    has_kana = kana_pattern.search(word)
    return has_kanji and has_kana


def save_kanji_and_kana():
    db.cursor.execute("SELECT `id`, `jap`, `url` FROM `voc` WHERE `kana` IS NOT NULL")
    res = db.cursor.fetchall()

    with open("save/kanji_and_kana.txt", "w", encoding="utf-8") as f:
        for r in res:
            if not is_japanese_word(r[1]):
                continue
            f.write(str(r[0]) + "\t" + r[2] + "\n")
            print(r[0], "\t", r[1])


def add_kana(id):
    global html
    soup = BeautifulSoup(html.pop(0), 'html.parser')
    soup = soup.select_one("#page_container > div > div > article > div > div.concept_light-wrapper > div.concept_light-readings > div")

    if soup is None:
        print(colorama.Fore.RED, "No soup", colorama.Fore.RESET)
        with open("save/error.txt", "a", encoding="utf-8") as f:
            f.write(str(id) + "\t" + words[index][1] + "\n")
        return

    furigana_span = []
    if soup.find('ruby') is not None:
        furigana_span = soup.find('span', {'class': 'furigana'}).find_all('rt')
        print(colorama.Fore.RED, "Found ruby", colorama.Fore.RESET)

    furigana_span += soup.find('span', {'class': 'furigana'}).find_all('span')
    kana_spans = soup.find('span', {'class': 'text'}).find_all('span')
    kanji = soup.find('span', {'class': 'text'}).text.strip()
    kana = ""

    index_kanji = 0
    for span in furigana_span:
        if not span.text.strip():
            if index_kanji >= len(kana_spans):
                break
            kana_text = kana_spans[index_kanji].text.strip()
            index_kanji += 1
        else:
            kana_text = span.text.strip()
        kana += kana_text


    if (len(furigana_span)>1) and (kana==soup.find('span', {'class': 'furigana'}).text.strip()):
        print(colorama.Fore.RED, "NO CHANGE", colorama.Fore.RESET)
        while True:
            time.sleep(10)


    print(kanji + "\n" + kana + "\n")
    db.cursor.execute("UPDATE `voc` SET `kana`=%s WHERE `id`=%s", (kana, id))
    db.conn.commit()


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
            time.sleep(10)



if __name__ == "__main__":
    processus = multiprocessing.Process(target=move_mouse)
    processus.start()
    colorama.init()
    db = ConnectionDatabase()


    html = []
    with open("save/kanji_and_kana.txt", "r", encoding="utf-8") as f:
        file = f.read().split("\n")
    words = []
    for line in file:
        elements = line.split('\t')
        words.append([elements[0], elements[1]])

    index = 0
    init_index()

    fetch_url(words[index][1])

    while index < len(words):
        print(colorama.Fore.CYAN, "{:.3f}".format((index / len(words)) * 100), "%\t", index, colorama.Fore.RESET)
        if index+1 >= len(words):
            add_kana(words[index][0])
        else:
            try:
                t1 = threading.Thread(target=fetch_url, args=(words[index+1][1],))
                t2 = threading.Thread(target=add_kana, args=(words[index][0],))
                t1.start()
                t2.start()
                t1.join()
                t2.join()
            except Exception as e:
                print(colorama.Fore.RED, "Erreur :", e, colorama.Style.RESET_ALL)
                exit(1)

        index += 1
        save_index(index)

    db.close()