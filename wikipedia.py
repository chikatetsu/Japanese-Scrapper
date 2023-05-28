import urllib.parse
import colorama
from bs4 import BeautifulSoup
from utils.TimeRemaining import TimeRemaining
from utils.bdd_class import ConnectionDatabase
from utils.index_class import Index
from utils.scrap_class import Scrap
from utils.shift_class import PressShift



def get_wiki_url(voc):
    global scrap
    global db

    soup = BeautifulSoup(scrap.get_one(), "lxml")
    wiki_url = soup.select("#p-lang-btn div div ul li.interwiki-fr a")

    if wiki_url is None or len(wiki_url) == 0:
        print(colorama.Fore.RED, "Pas d'url dans cette page", colorama.Fore.RESET)
        return False

    wiki_url = wiki_url[0]['href'].replace("https://fr.wikipedia.org/", "")
    print(colorama.Fore.YELLOW, wiki_url, colorama.Fore.RESET)
    trad = wiki_url.replace("wiki/", "")
    trad = urllib.parse.unquote(trad, encoding='utf-8')
    trad = trad.replace("_", " ")
    print(colorama.Fore.GREEN, trad, "\n", colorama.Fore.RESET)

    try:
        db.cursor.execute("UPDATE `voc` SET `fra`=%s, `url`=%s, `difficulteJP`=0 WHERE `id`=%s", (trad, wiki_url, voc[0]))
        db.conn.commit()
    except Exception as e:
        print(colorama.Fore.RED, "Un problème est survenu lors de l'insertion dans la base de données :", e, colorama.Fore.RESET)
        with open("save/error.txt", "a", encoding="utf-8") as f:
            f.write(str(voc[0])+"\thttps://jisho.org/"+voc[1]+"\n")
        return False
    return True



def get_element_in_file():
    with open("save/new_wiki_url.txt", "r", encoding="utf-8") as f:
        file = f.read().split("\n")
    result = []
    for line in file:
        elements = line.split('\t')
        if len(elements) >= 2:
            result.append([elements[0], elements[1]])
    return result



def save_element_in_file(data):
    with open("save/new_wiki_url.txt", "w", encoding="utf-8") as f:
        for line in data:
            f.write(str(line[0]) + "\t" + str(line[1]) + "\n")



if __name__ == "__main__":
    colorama.init()
    PressShift()
    scrap = Scrap("https://ja.wikipedia.org/")
    index = Index("save/processWiki.txt")
    db = ConnectionDatabase()

    wiki = get_element_in_file()
    tm = TimeRemaining(len(wiki))

    while index.value < len(wiki):
        tm.length = len(wiki)
        tm.print_time_and_percent(index.value)
        print(wiki[index.value][0])
        scrap.fetch_url(wiki[index.value][1])
        if get_wiki_url(wiki[index.value]):
            wiki.pop(index.value)
            save_element_in_file(wiki)
        else:
            index.increment()
            index.save()
    db.close()
