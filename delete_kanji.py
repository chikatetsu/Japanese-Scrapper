import time
from bs4 import BeautifulSoup
import threading
import colorama
import requests
from utils.bdd_class import ConnectionDatabase
from utils.index_class import Index


def is_written_in_kana(voc):
    global html

    soup = BeautifulSoup(html.pop(0), "html.parser")
    container = soup.select_one("#page_container > div > div > article > div > div.concept_light-meanings.medium-9.columns > div > div.meaning-wrapper")
    if container is None:
        print(colorama.Fore.CYAN, "{:.3f}".format((index.value / total) * 100), "%\t", index.value, colorama.Fore.RESET)
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
        print(colorama.Fore.CYAN, "{:.3f}".format((index.value / total) * 100), "%\t", index.value, colorama.Fore.RESET)
        print(voc[2], "\t" + voc[0] + "\n")


        # db.cursor.execute("UPDATE `voc` SET `difficulte`=NULL, `jap`=`kana`, `kana`=NULL WHERE `id`=%s", ())
        # db.conn.commit()


        return True


def delete_dead_url(soup, voc):
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


def fetch_url(url):
    global html
    connected = False
    error_message_displayed = False

    while not connected:
        try:
            response = requests.get("https://jisho.org/" + url, timeout=None)
            connected = True
            html.append(response.content)

        except requests.exceptions.RequestException:
            if not error_message_displayed:
                print(colorama.Fore.RED, "ERREUR DE CONNEXION : Veuillez vérifier votre connexion internet", colorama.Fore.RESET)
                error_message_displayed = True
            time.sleep(10)



if __name__ == '__main__':
    colorama.init()
    #MoveMouse()

    db = ConnectionDatabase()

    db.cursor.execute("SELECT `url`,`fra`,`id` FROM `voc` WHERE `kana` IS NOT NULL ORDER BY `id` ASC")
    voc = db.cursor.fetchall()

    db.cursor.execute("SELECT COUNT(*) FROM `voc` WHERE `kana` IS NOT NULL")
    total = db.cursor.fetchone()[0]

    saved_url = get_all_saved_url()
    html = []

    index = Index("save/processDelete.txt")
    index.value = filter_index(index.value, voc)
    fetch_url(voc[index.value][0])

    while index.value < len(voc):
        if index.value + 1 >= len(voc):
            is_written_in_kana(voc[index.value][1])
        else:
            t1 = threading.Thread(target=fetch_url, args=(voc[filter_index(index.value+1, voc)][0],))
            t2 = threading.Thread(target=is_written_in_kana, args=(voc[index.value],))
            t1.start()
            t2.start()
            t1.join()
            t2.join()
        old_index = index.value+1
        index.value = filter_index(index.value+1, voc)
        if old_index != index.value:
            print(colorama.Fore.CYAN, "{:.3f}".format((index.value / total) * 100), "%\t", index.value, colorama.Fore.RESET)
            print(colorama.Fore.GREEN, "Index skipped\n", colorama.Fore.RESET)
        index.save()

    db.close()
