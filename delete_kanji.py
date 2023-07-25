from bs4 import BeautifulSoup
import threading
import colorama
from utils.time_remaining import TimeRemaining
from utils.bdd_class import ConnectionDatabase
from utils.index_class import Index
from utils.scrap_class import Scrap
from utils.shift_class import PressShift



def is_written_in_kana(voc):
    """ Check if the kanji is written in kana """
    global scrap

    soup = BeautifulSoup(scrap.get_one(), "html.parser")
    container = soup.select_one("#page_container > div > div > article > div > div.concept_light-meanings.medium-9.columns > div > div.meaning-wrapper")
    if container is None:
        print(colorama.Fore.RED, voc[2], "\t" + voc[0] + "\n", colorama.Fore.RESET)
        delete_dead_url(soup, voc)
        return False

    fra = container.select_one("div > span.meaning-meaning").text.strip()
    if fra != voc[1] :
        return False

    tag = container.select_one('div > span.supplemental_info > span.sense-tag.tag-tag')
    if tag is None:
        return False
    tag = tag.text.strip()
    if "Usually written using kana alone" in tag:
        with open("save/kanjiless.txt", "a", encoding="utf-8") as f:
            f.write(str(voc[2]) + "\t" + voc[0] + "\n")
        print(voc[2], "\t" + voc[0] + "\n")

        # db.cursor.execute("UPDATE `voc` SET `difficulte`=NULL, `jap`=`kana`, `kana`=NULL WHERE `id`=%s", ())
        # db.conn.commit()

        return True



def delete_dead_url(soup, voc):
    """ Delete the url of the word if it doesn't exist anymore """
    global db

    page = soup.select_one("h1")
    if page is None:
        with open("save/error.txt", "a", encoding="utf-8") as f:
            f.write(str(voc[2]) + "\t" + voc[0] + "\n")
            return

    page = page.text.strip()
    if page == "The page you were looking for doesn't exist.":
        db.cursor.execute("UPDATE `voc` SET `url`=NULL WHERE `id`=%s", (voc[2],))
        db.conn.commit()



def get_all_saved_url():
    """ Gets urls of kanji that are written in kana """
    with open("save/kanjiless.txt", "r", encoding="utf-8") as f:
        ids = []
        for line in f:
            id, _ = line.split('\t')
            ids.append(int(id))
        return ids


def filter_index(i, voc):
    global saved_url
    while voc[i][2] in saved_url:
        i += 1
    return i



if __name__ == '__main__':
    """ Gets all kanji that are written in kana and save it in a file """
    colorama.init()
    PressShift()
    scrap = Scrap("https://jisho.org/")
    db = ConnectionDatabase()

    # Gets all kanji (because they have kana)
    db.cursor.execute("SELECT `url`,`fra`,`id` FROM `voc` WHERE `kana` IS NOT NULL ORDER BY `id`")
    voc = db.cursor.fetchall()

    tm = TimeRemaining(len(voc))
    saved_url = get_all_saved_url()

    index = Index("save/processDelete.txt")
    index.value = filter_index(index.value, voc)
    scrap.fetch_url(voc[index.value][0])

    while index.value < len(voc):
        tm.print_percent(index.value)
        if index.value + 1 >= len(voc):
            is_written_in_kana(voc[index.value][1])
        else:
            t1 = threading.Thread(target=scrap.fetch_url, args=(voc[filter_index(index.value+1, voc)][0],))
            t2 = threading.Thread(target=is_written_in_kana, args=(voc[index.value],))
            t1.start()
            t2.start()
            t1.join()
            t2.join()
        old_index = index.value+1
        index.value = filter_index(index.value+1, voc)
        if old_index != index.value:
            print(colorama.Fore.GREEN, "Index skipped\n", colorama.Fore.RESET)
        index.save()

    db.close()
