import webbrowser
from bs4 import BeautifulSoup
import colorama
from utils.TimeRemaining import TimeRemaining
from utils.bdd_class import ConnectionDatabase
from utils.index_class import Index
from utils.scrap_class import Scrap
from utils.shift_class import PressShift



def fetch_all_words(words):
    global scrap
    for word in words:
        scrap.fetch_url(word)


def get_trad(id):
    global scrap

    nb_op_failed = 0
    result_fra = ""
    while len(scrap.html) != 0:
        soup = BeautifulSoup(scrap.get_one(), "html.parser")
        fra = soup.select('#articleWRD table.WRD tr.even td.ToWrd')


        if fra is None or len(fra) == 0:
            nb_op_failed += 1
            print(colorama.Fore.RED, "Impossible de trouver la traduction pour le mot à l'id ", id, colorama.Fore.RESET)
            with open("save/trad_err.txt", "a", encoding="utf-8") as f:
                f.write(str(id) + '\n')
            scrap.clear_html()

            if nb_op_failed < 20:
                return False
            with open("save/err.html", "w", encoding="utf-8") as f:
                f.write(str(soup))

            if input("Voir le html? (o/n)") == "o":
                webbrowser.open("C:/Users/kakap/PycharmProjects/scrap/save/err.html")
            if input("Sauter cet index la prochaine fois? (o/n)") == "o":
                with open("save/processWordreference.txt", "w", encoding="utf-8") as f:
                    f.write(str(id))
            return False


        nb_op_failed = 0
        if len(result_fra) != 0:
            result_fra += ';'
        k = 0
        while k < len(fra):
            if fra[k].contents[0].text.strip().endswith('vtr'):
                break
            if fra[k].contents[0].text.strip().endswith('vi'):
                break
            k += 1
        if k == len(fra):
            k = 0
        result_fra += fra[k].contents[0].text.rstrip()

    with open("save/processWordreference.txt", "w", encoding="utf-8") as f:
        f.write(str(id))
    print(colorama.Fore.GREEN, result_fra+"\n", colorama.Fore.RESET)
    db.cursor.execute("UPDATE `voc` SET `fra`=%s, `difficulteJP`=0 WHERE `id`=%s", (result_fra, id))
    db.conn.commit()
    return True



def clean_db():
    db.cursor.execute("UPDATE `voc` SET `fra`=REPLACE(`fra`,'\n','') WHERE `fra` LIKE '%\n%'")
    db.cursor.execute("UPDATE `voc` SET `fra`=REPLACE(`fra`,'\r','') WHERE `fra` LIKE '%\r%'")
    db.cursor.execute("UPDATE `voc` SET `fra`=REPLACE(`fra`,' ;',';') WHERE `fra` LIKE '% ;%'")
    db.cursor.execute("UPDATE `voc` SET `fra`=REPLACE(`fra`,'; ',';') WHERE `fra` LIKE '%; %'")
    db.conn.commit()



if __name__ == '__main__':
    PressShift()
    colorama.init()
    scrap = Scrap("https://www.wordreference.com/enfr/")
    index = Index("save/processReverso.txt")
    db = ConnectionDatabase()

    clean_db()
    db.cursor.execute("SELECT * FROM `voc` WHERE `fra` REGEXP '^(to [^ ]+;)*(to [^ ]+)$'")
    # db.cursor.execute("SELECT `id`, `fra` FROM `voc` WHERE `fra` NOT LIKE '% %' AND (`difficulteJP`!=0 OR `difficulteJP` IS NULL) AND `id`>=%s AND `url` LIKE '%\%%' AND `url` NOT LIKE 'wiki%' ORDER BY `id`", (index.value,))
    voc = db.cursor.fetchall()
    tm = TimeRemaining(len(voc))

    allFra = []
    while index.value < len(voc):
        tm.length = len(voc)
        tm.print_time(index.value, len(allFra))
        tm.print_percent(index.value)

        allFra = voc[index.value][1].split(';')
        print(voc[index.value][0], "\t", allFra)

        fetch_all_words(allFra)
        if get_trad(voc[index.value][0]):
            voc.pop(index.value)
        else:
            index.increment()
            index.save()

    db.close()
