import os
import re
import threading
import time
import colorama
from bs4 import BeautifulSoup
from translate import Translator
from utils.TimeRemaining import TimeRemaining
from utils.bdd_class import ConnectionDatabase
from utils.scrap_class import Scrap
from utils.shift_class import PressShift



def format_word(word):
    word = word.lower() #WORD

    # (...)
    paren_patthern = r"\([^()]*\)"
    temp = re.sub(paren_patthern, "", word)
    if temp == "":
        temp = word.replace("(", "").replace(")", "")
    word = temp

    # <...>
    chevr_patthern = r"\<[^<>]*\>"
    temp = re.sub(chevr_patthern, "", word)
    if temp == "":
        temp = word.replace("<", "").replace(">", "")
    word = temp

    # *.!?, ...
    letter_patthern = r"(\W|_)"
    word = re.sub(letter_patthern, "", word)

    #roman_patthern = r"[I|V|X]\." #IV.
    return word.strip()



def get_trad_wordreference(eng):
    global scrap_wr

    scrap_wr.fetch_url(eng)
    soup = BeautifulSoup(scrap_wr.get_one(), "html.parser")
    fra = soup.select('#articleWRD table.WRD tr.even td.ToWrd')

    if fra is None or len(fra) == 0:
        return get_trad_mymemory(eng)
    return fra[0].contents[0].text.rstrip()



def get_trad_mymemory(eng):
    global scrap_mm

    scrap_mm.fetch_url(eng.replace(" ", "-"))
    soup = BeautifulSoup(scrap_mm.get_one(), "html.parser")
    fra = soup.select('#resall div div div div.target p span.text')
    org = soup.select('#resall div div div div.source p span.text')
    if org is None or len(org) == 0:
        print(colorama.Fore.RED, "DIDN'T FIND THE ENGLISH WORD", colorama.Fore.RESET)
        with open("save/err.html", "w", encoding="utf-8") as f:
            f.write(str(soup))
        return get_trad(eng)
    if format_word(org[0].contents[0].text.rstrip()) != format_word(eng):
        print(colorama.Fore.YELLOW, "NOT THE SAME ENGLISH WORD :", org[0].contents[0].text.rstrip(), colorama.Fore.RESET)
        with open("save/err.html", "w", encoding="utf-8") as f:
            f.write(str(soup))
        return get_trad(eng)

    if fra is None or len(fra) == 0:
        print(colorama.Fore.YELLOW, "using original get_trad()", colorama.Fore.RESET)
        with open("save/err.html", "w", encoding="utf-8") as f:
            f.write(str(soup))
        return get_trad(eng)

    try:
        content = fra[0].contents[0].text.rstrip()
    except:
        print(colorama.Fore.YELLOW, "using original get_trad()", colorama.Fore.RESET)
        return get_trad(eng)

    if content == "":
        print(colorama.Fore.YELLOW, "using original get_trad()", colorama.Fore.RESET)
        with open("save/err.html", "w", encoding="utf-8") as f:
            f.write(str(soup))
        return get_trad(eng)
    print(colorama.Fore.YELLOW, content, colorama.Fore.RESET)
    return content



# def get_trad(eng):
#     global translator
#     translation = ""
#     def translate():
#         nonlocal translation
#         while True:
#             try:
#                 translation = translator.translate(eng)
#                 return
#             except:
#                 print(colorama.Fore.RED, "ERROR WHEN TRYING TO TRANSLATE. CHANGING PROXY...", colorama.Fore.RESET)
#                 get_new_proxy()
#
#     translation_thread = threading.Thread(target=translate)
#     start_time = time.time()
#
#     while True:
#         translation_thread.start()
#         translation_thread.join(timeout=120)
#
#         if time.time() - start_time >= 120:
#             print(colorama.Fore.RED, "CONNECTION TIMEOUT. CHANGING PROXY...", colorama.Fore.RESET)
#             get_new_proxy()
#             translation_thread = threading.Thread(target=translate)
#             start_time = time.time()
#             continue
#
#         if not translation.startswith("MYMEMORY WARNING"):
#             return translation
#
#         print(colorama.Fore.RED, "LIMIT OF REQUEST. CHANGING PROXY...", colorama.Fore.RESET)
#         get_new_proxy()



def get_trad(eng):
    global translator
    is_message_displayed = False

    while True:
        translation = translator.translate(eng)
        if not translation.startswith("MYMEMORY WARNING"):
            return translation
        if not is_message_displayed:
            print(colorama.Fore.RED, translation, colorama.Fore.RESET)
            is_message_displayed = True
        time.sleep(10)



def update_db(id, fra):
    db.cursor.execute("UPDATE `voc` SET `fra`=%s, `difficulteJP`=0 WHERE `id`=%s", (fra, id))
    db.conn.commit()


def clean_db():
    db.cursor.execute("UPDATE `voc` SET `fra`=REPLACE(`fra`,'\n','') WHERE `fra` LIKE '%\n%'")
    db.cursor.execute("UPDATE `voc` SET `fra`=REPLACE(`fra`,'\r','') WHERE `fra` LIKE '%\r%'")
    db.cursor.execute("UPDATE `voc` SET `fra`=REPLACE(`fra`,' ;',';') WHERE `fra` LIKE '% ;%'")
    db.cursor.execute("UPDATE `voc` SET `fra`=REPLACE(`fra`,'; ',';') WHERE `fra` LIKE '%; %'")
    db.conn.commit()



def get_new_proxy():
    with open("http_proxies.txt", "r", encoding="utf-8") as f:
        lines = f.read().split("\n")
    if len(lines) == 0:
        print(colorama.Fore.RED, "NO MORE PROXIES IN THE FILE. PLEASE RESTART WITH NEW PROXIES", colorama.Fore.RESET)
        while True:
            time.sleep(10)
    proxy_host, proxy_port = lines[0].split(':')
    print(colorama.Fore.MAGENTA, f"NEW PROXY CONNECTION : {proxy_host}:{proxy_port}", colorama.Fore.RESET)
    os.environ['http_proxy'] = f"https://{proxy_host}:{proxy_port}"
    os.environ['https_proxy'] = f"https://{proxy_host}:{proxy_port}"
    with open("http_proxies.txt", "w", encoding="utf-8") as f:
        for l in lines[1:]:
            f.write(l + "\n")
    with open("http_proxies.txt", "a", encoding="utf-8") as f:
        f.write(lines[0])



if __name__ == "__main__":
    PressShift()
    colorama.init()
    scrap_wr = Scrap("https://www.wordreference.com/enfr/")
    scrap_mm = Scrap("https://mymemory.translated.net/en/English/French/")
    #get_new_proxy()
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
                newFra += get_trad_mymemory(eng)
            else:
                newFra += get_trad_wordreference(eng)
        update_db(voc[0], newFra)
        print(colorama.Fore.GREEN, newFra, colorama.Fore.RESET, '\n')
    db.close()
