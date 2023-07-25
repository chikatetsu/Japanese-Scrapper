import re
import time
import urllib.parse

import colorama
from bs4 import BeautifulSoup
from translate import Translator
from utils.time_remaining import TimeRemaining
from utils.bdd_class import ConnectionDatabase
from utils.scrap_class import Scrap
from utils.shift_class import PressShift



def format_word(word):
    """Formate le mot afin d'enlever les caractères en trop"""
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

    # *.!?,...
    letter_patthern = r"[^a-z0-9 '\-àâäéèêëîïôöùûüÿçæāēīōū]"
    word = re.sub(letter_patthern, "", word)

    #roman_patthern = r"[I|V|X]\." #IV.
    return word.strip()


def simplify_fra(fra):
    """Transforme la traduction en dictionnaire"""
    paren_patthern = r"\([^()]*\)"
    temp = re.sub(paren_patthern, "", fra)
    if temp == "":
        temp = fra.replace("(", "").replace(")", "")
    fra = temp
    fra = fra.replace(",", ";")
    tab_fra = fra.split(";")
    dict_fra = dict()
    for w in tab_fra:
        w = format_word(w)
        if w == "":
            continue
        if w not in dict_fra:
            dict_fra[w] = 0
        dict_fra[w] += 1

    dict_fra = sort_dict(dict_fra)
    for i in dict_fra:
        print(f"'{i}' : {dict_fra[i]}")

    return get_keys_by_value(dict_fra)


def sort_dict(dictionary):
    return dict(sorted(dictionary.items(), key=lambda x: x[1], reverse=True))


def get_keys_by_value(dictionary):
    dictionary = merge_similar_words(dictionary)
    items = list(dictionary.items())
    if len(items) == 0:
        return ""
    first_key, first_value = items[0]
    result = [first_key]

    for key, value in items[1:]:
        if value==first_value or value==first_value-1:
            result.append(key)
        if value < first_value-1:
            break
        if len(result) == 5:
            break

    return ";".join(result[:5])



def merge_similar_words(dictionary):
    to_delete = {}

    for i, key1 in enumerate(dictionary.keys()):
        for j, key2 in enumerate(dictionary.keys()):
            if i <= j:
                continue
            if key2 in to_delete or key1 in to_delete:
                continue

            if similarity_percentage(key1, key2) < 75:
                continue
            print(colorama.Fore.MAGENTA, key1.upper(), "et", key2.upper(), "sont similaire", colorama.Fore.RESET)

            if dictionary[key1] > dictionary[key2]:
                dictionary[key1] += dictionary[key2]
                to_delete[key2] = True
                continue

            if dictionary[key2] > dictionary[key1]:
                dictionary[key2] += dictionary[key1]
                to_delete[key1] = True
                continue

            if len(key1) > len(key2):
                dictionary[key2] += dictionary[key1]
                to_delete[key1] = True
                continue

            dictionary[key1] += dictionary[key2]
            to_delete[key2] = True

    for key in to_delete.keys():
        del dictionary[key]

    return sort_dict(dictionary)


def similarity_percentage(word1, word2):
    # Calcul de la distance de Levenshtein
    distance = levenshtein_distance(word1, word2)

    # Calcul du pourcentage de similitude
    max_length = max(len(word1), len(word2))
    similarity = (max_length - distance) / max_length * 100

    return similarity


def levenshtein_distance(word1, word2):
    # Initialisation de la matrice
    matrix = [[0] * (len(word2) + 1) for _ in range(len(word1) + 1)]

    # Remplissage de la première ligne et de la première colonne
    for i in range(len(word1) + 1):
        matrix[i][0] = i
    for j in range(len(word2) + 1):
        matrix[0][j] = j

    # Calcul de la distance de Levenshtein
    for i in range(1, len(word1) + 1):
        for j in range(1, len(word2) + 1):
            if word1[i - 1] == word2[j - 1]:
                cost = 0
            else:
                cost = 1
            matrix[i][j] = min(matrix[i - 1][j] + 1,  # Suppression
                               matrix[i][j - 1] + 1,  # Insertion
                               matrix[i - 1][j - 1] + cost)  # Substitution

    return matrix[len(word1)][len(word2)]


def get_trad_jisho(url, jap, id):
    """Récupère les traductions en plus sur jisho.org"""
    global scrap_jisho
    global db
    scrap_jisho.fetch_url(url)
    soup = BeautifulSoup(scrap_jisho.get_one(), "html.parser")
    eng = soup.select("#page_container div div article div div.concept_light-meanings.medium-9.columns div div.meaning-wrapper div span.meaning-meaning")
    result = []

    if eng is None or len(eng) == 0:
        newurl = urllib.parse.quote("word/"+jap)
        scrap_jisho.fetch_url(newurl)
        soup = BeautifulSoup(scrap_jisho.get_one(), "html.parser")
        eng = soup.select("#page_container div div article div div.concept_light-meanings.medium-9.columns div div.meaning-wrapper div span.meaning-meaning")
        if eng is None or len(eng) == 0:
            db.cursor.execute("UPDATE `voc` SET `url`='' WHERE `id`=%s", (id,))
            db.conn.commit()
            return []
        db.cursor.execute("UPDATE `voc` SET `url`=%s WHERE `id`=%s", (newurl, id))
        db.conn.commit()

    for w in eng:
        word = w.contents[0].text.rstrip()
        temp = re.search(r"[a-zA-Z0-9]", word)
        if temp is not None:
            result += word.split(";")
        else:
            print(colorama.Fore.RED, f"'{word}' denied", colorama.Fore.RESET)
    return [w.strip() for w in result]


def get_trad_wordreference(eng):
    """Récupère toutes les traductions sur wordreference"""
    global scrap_wr
    scrap_wr.fetch_url(eng)
    soup = BeautifulSoup(scrap_wr.get_one(), "html.parser")
    fra = soup.select("#articleWRD table.WRD tr.even td.ToWrd")

    if fra is None or len(fra) == 0:
        global scrap_mm_en, translator_en
        return get_trad_mymemory(scrap_mm_en, translator_en, eng)

    result = []
    for i in range(len(fra)):
        result.append(fra[i].contents[0].text.rstrip())
    print(colorama.Fore.YELLOW, f"'{eng}' translated with WORDREFERENCE", colorama.Fore.RESET)
    return ";".join(result)


def get_trad_mymemory(scrap, translator, word):
    scrap.fetch_url(word.replace(" ", "-"))
    soup = BeautifulSoup(scrap.get_one(), "html.parser")
    fra = soup.select('#resall div div div div.target p span.text')
    org = soup.select('#resall div div div div.source p span.text')
    if org is None or len(org) == 0:
        return get_trad(translator, word)
    try:
        if format_word(org[0].contents[0].text.rstrip()) != format_word(word):
            return get_trad(translator, word)
    except:
        return get_trad(translator, word)

    if fra is None or len(fra) == 0:
        return get_trad(translator, word)

    try:
        content = fra[0].contents[0].text.rstrip()
    except:
        return get_trad(translator, word)

    if content == "":
        return get_trad(translator, word)
    print(colorama.Fore.YELLOW, f"'{word}' translated with MYMEMORY", colorama.Fore.RESET)
    return content


def get_trad(translator, jap):
    is_message_displayed = False

    try:
        while True:
            translation = translator.translate(jap)
            if not translation.startswith("MYMEMORY WARNING"):
                print(colorama.Fore.YELLOW, f"'{jap}' translated with TRANSLATOR", colorama.Fore.RESET)
                return translation
            if not is_message_displayed:
                print(colorama.Fore.RED, translation, colorama.Fore.RESET)
                is_message_displayed = True
            time.sleep(10)
    except:
        return ""


def update_db(id, fra):
    db.cursor.execute("UPDATE `voc` SET `fra`=%s, `isTranslated`=1 WHERE `id`=%s", (fra, id))
    db.conn.commit()



if __name__ == "__main__":
    PressShift()
    colorama.init()
    scrap_jisho = Scrap("https://jisho.org/")
    scrap_wr = Scrap("https://www.wordreference.com/enfr/")
    scrap_mm_en = Scrap("https://mymemory.translated.net/en/English/French/")
    translator_en = Translator(from_lang="en", to_lang="fr")
    scrap_mm_ja = Scrap("https://mymemory.translated.net/en/Japanese/French/")
    translator_ja = Translator(from_lang="ja", to_lang="fr")

    db = ConnectionDatabase()
    db.cursor.execute("SELECT `id`, `url`, `jap` FROM `voc` WHERE `isTranslated`=0")
    vocs = db.cursor.fetchall()
    tr = TimeRemaining(len(vocs))

    db.cursor.execute("SELECT COUNT(*) FROM `voc`")
    tr_forall = TimeRemaining(db.cursor.fetchone()[0])
    db.cursor.execute("SELECT COUNT(*) FROM `voc` WHERE `isTranslated`=1")
    len_translated = db.cursor.fetchone()[0]

    jisho = ['element']
    for voc in vocs:
        tr.print_time(vocs.index(voc), len(jisho))
        tr_forall.print_percent(len_translated + vocs.index(voc))

        jisho = get_trad_jisho(voc[1], voc[2], voc[0])
        if jisho is None or len(jisho) == 0:
            print(colorama.Back.RED, voc[0], "No translation found for", voc[2], colorama.Back.RESET)
            continue
        print(voc[0], '\t', jisho)

        newFra = []
        for eng in jisho:
            if eng.startswith("to "):
                eng = eng[3:]
            if " " in eng:
                newFra.append(get_trad_mymemory(scrap_mm_en, translator_en, eng))
            else:
                newFra.append(get_trad_wordreference(eng))
        newFra.append(get_trad_mymemory(scrap_mm_ja, translator_ja, voc[2]))
        final = simplify_fra(";".join(newFra))

        if final == "":
            print(colorama.Back.RED, "No translation found for", voc[2], colorama.Back.RESET)
            continue
        print(colorama.Fore.GREEN, voc[2], ":", final, colorama.Fore.RESET, '\n\n')
        update_db(voc[0], final)
    db.close()
