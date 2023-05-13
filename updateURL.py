from bs4 import BeautifulSoup
import threading
import time
import colorama
import requests
from utils.bdd_class import ConnectionDatabase


def get_url(id):
    global html
    global db

    soup = BeautifulSoup(html.pop(0), "html.parser")
    url = soup.select_one("#primary div.exact_block div.concept_light.clearfix a.light-details_link")['href']
    url = url[12:]

    print(url)
    db.cursor.execute("UPDATE `voc` SET `url`=%s WHERE `id`=%s", (url,id))
    db.conn.commit()



def print_voc(index, end):
    print(colorama.Fore.CYAN, "{:.3f}".format((index/end)*100), "%\t", index, colorama.Fore.RESET)



def fetch_url(url):
    global html
    connected = False
    error_message_displayed = False

    while not connected:
        try:
            response = requests.get("https://jisho.org/search/" + url, timeout=None)
            connected = True
            html.append(response.content)

        except requests.exceptions.RequestException as e:
            if not error_message_displayed:
                print(colorama.Fore.RED, "ERREUR DE CONNEXION : Veuillez vérifier votre connexion internet", colorama.Fore.RESET)
                error_message_displayed = True
            time.sleep(30)



if __name__ == '__main__':
    colorama.init()
    db = ConnectionDatabase()

    db.cursor.execute("SELECT `id`,`jap` FROM `voc` WHERE `url` IN (SELECT `url` FROM `voc` GROUP BY `url` HAVING COUNT(`url`) > 1)")
    res = db.cursor.fetchall()

    html = []
    fetch_url(res[0][1])

    for i in range(len(res)):
        if i+1 >= len(res):
            get_url(res[i][0])
        else:
            t1 = threading.Thread(target=fetch_url, args=(res[i+1][1],))
            t2 = threading.Thread(target=get_url, args=(res[i][0],))
            t1.start()
            t2.start()
            t1.join()
            t2.join()
        print_voc(i, len(res))
        print(res[i][0], "\n")

    db.close()
