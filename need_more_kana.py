import threading
import colorama
import regex as re
from bs4 import BeautifulSoup
import time
from utils.TimeRemaining import TimeRemaining
from utils.bdd_class import ConnectionDatabase
from utils.index_class import Index
from utils.scrap_class import Scrap
from utils.shift_class import PressShift



def get_words():
    """ Get all the words that need more kana from the file """
    with open("save/kanji_and_kana.txt", "r", encoding="utf-8") as f:
        file = f.read().split("\n")
    result = []
    for line in file:
        elements = line.split('\t')
        result.append([elements[0], elements[1]])
    return result


def is_japanese_word(word):
    """ If a japanese word contains kanji and kana, return True. Else, return False """
    kanji_pattern = re.compile(r'[\p{Han}\p{Common}]+')
    kana_pattern = re.compile(r'[\p{Hiragana}\p{Katakana}ー]+')
    has_kanji = kanji_pattern.search(word)
    has_kana = kana_pattern.search(word)
    return has_kanji and has_kana


def save_kanji_and_kana():
    """ Save all the kanji and kana in a file """
    db.cursor.execute("SELECT `id`, `jap`, `url` FROM `voc` WHERE `kana` IS NOT NULL")
    res = db.cursor.fetchall()

    with open("save/kanji_and_kana.txt", "w", encoding="utf-8") as f:
        for r in res:
            if not is_japanese_word(r[1]):
                continue
            f.write(str(r[0]) + "\t" + r[2] + "\n")
            print(r[0], "\t", r[1])


def add_kana(id):
    """ Add the kana of a word in the database """
    global scrap
    soup = BeautifulSoup(scrap.get_one(), 'html.parser')
    soup = soup.select_one("#page_container > div > div > article > div > div.concept_light-wrapper > div.concept_light-readings > div")

    if soup is None:
        print(colorama.Fore.RED, "No soup", colorama.Fore.RESET)
        with open("save/error.txt", "a", encoding="utf-8") as f:
            f.write(str(id) + "\t" + words[index.value][1] + "\n")
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



if __name__ == "__main__":
    PressShift()
    colorama.init()
    index = Index("save/processNMK.txt")
    scrap = Scrap("https://jisho.org/")
    db = ConnectionDatabase()

    words = get_words()
    tm = TimeRemaining(len(words))
    scrap.fetch_url(words[index.value][1])

    while index.value < len(words):
        tm.print_percent(index.value)
        if index.value+1 >= len(words):
            add_kana(words[index.value][0])
        else:
            t1 = threading.Thread(target=scrap.fetch_url, args=(words[index.value+1][1],))
            t2 = threading.Thread(target=add_kana, args=(words[index.value][0],))
            t1.start()
            t2.start()
            t1.join()
            t2.join()
        index.increment()
        index.save()
    db.close()