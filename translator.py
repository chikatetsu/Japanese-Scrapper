import colorama
from bs4 import BeautifulSoup
from translate import Translator
from utils.TimeRemaining import TimeRemaining
from utils.bdd_class import ConnectionDatabase
from utils.scrap_class import Scrap
from utils.shift_class import PressShift



def get_trad_wordreference(eng):
    global scrap

    scrap.fetch_url(eng)
    soup = BeautifulSoup(scrap.get_one(), "html.parser")
    fra = soup.select('#articleWRD table.WRD tr.even td.ToWrd')

    if fra is None or len(fra) == 0:
        return get_trad(eng)
    return fra[0].contents[0].text.rstrip()



def get_trad(eng):
    global translator
    translation = translator.translate(eng)
    if translation.startswith("MYMEMORY WARNING"):
        print(colorama.Fore.RED, translation, colorama.Fore.RESET)
        while True:
            pass
    return translation


def update_db(id, fra):
    db.cursor.execute("UPDATE `voc` SET `fra`=%s, `difficulteJP`=0 WHERE `id`=%s", (fra, id))
    db.conn.commit()


def clean_db():
    db.cursor.execute("UPDATE `voc` SET `fra`=REPLACE(`fra`,'\n','') WHERE `fra` LIKE '%\n%'")
    db.cursor.execute("UPDATE `voc` SET `fra`=REPLACE(`fra`,'\r','') WHERE `fra` LIKE '%\r%'")
    db.cursor.execute("UPDATE `voc` SET `fra`=REPLACE(`fra`,' ;',';') WHERE `fra` LIKE '% ;%'")
    db.cursor.execute("UPDATE `voc` SET `fra`=REPLACE(`fra`,'; ',';') WHERE `fra` LIKE '%; %'")
    db.conn.commit()



if __name__ == "__main__":
    PressShift()
    colorama.init()
    scrap = Scrap("https://www.wordreference.com/enfr/")
    translator = Translator(to_lang="fr")
    db = ConnectionDatabase()

    clean_db()
    db.cursor.execute("SELECT * FROM `voc` WHERE `difficulteJP`!=0 OR `difficulteJP` IS NULL")
    vocs = db.cursor.fetchall()
    tr = TimeRemaining(len(vocs))

    db.cursor.execute("SELECT COUNT(*) FROM `voc`")
    tr_forall = TimeRemaining(db.cursor.fetchone()[0])
    db.cursor.execute("SELECT COUNT(*) FROM `voc` WHERE `difficulteJP`=0")
    len_translated = db.cursor.fetchone()[0]

    allFra = []
    for voc in vocs:
        tr.print_time(vocs.index(voc), len(allFra))
        tr_forall.print_percent(len_translated + vocs.index(voc))

        allFra = voc[1].split(';')
        print(voc[0], "\t", allFra)

        newFra = ""
        for eng in allFra:
            if newFra != "":
                newFra += ";"
            if " " in eng:
                newFra += get_trad(eng)
            else:
                newFra += get_trad_wordreference(eng)
        update_db(voc[0], newFra)
        print(colorama.Fore.GREEN, newFra, colorama.Fore.RESET, '\n')
    db.close()
