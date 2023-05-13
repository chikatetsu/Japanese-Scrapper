import webbrowser
import colorama
from utils.bdd_class import ConnectionDatabase


def remove_id_from_errors():
    id_to_remove = ids[0]
    while id_to_remove in ids:
        ids.remove(id_to_remove)

    with open("save/trad_err.txt", "w", encoding="utf-8") as f:
        f.write('\n'.join(ids))


if __name__ == '__main__':
    with open("save/trad_err.txt", "r", encoding="utf-8") as f:
        ids = f.read()
    ids = ids.split('\n')
    db = ConnectionDatabase()
    colorama.init()

    while len(ids) > 0:
        print(colorama.Fore.CYAN, "Restant :", len(ids), colorama.Fore.RESET)

        db.cursor.execute("SELECT `id`,`fra`,`jap`,`kana`,`difficulteJP`,`url` FROM `voc` WHERE `id`=%s", (ids[0],))
        voc = db.cursor.fetchone()

        if voc[4] == 0:
            print(colorama.Fore.GREEN, voc[0], voc[1], voc[2], voc[3], colorama.Fore.RESET)
            remove_id_from_errors()
            continue
        if "%" not in voc[5]:
            print(colorama.Fore.GREEN, voc[0], voc[1], voc[2], voc[3], colorama.Fore.RESET)
            remove_id_from_errors()
            continue
        if voc[5].startswith("wiki/"):
            print(colorama.Fore.GREEN, voc[0], voc[1], voc[2], voc[3], colorama.Fore.RESET)
            remove_id_from_errors()
            continue


        print(voc)
        webbrowser.open("https://jisho.org/" + voc[5])
        for eng in voc[1].split(';'):
            webbrowser.open("https://www.wordreference.com/enfr/" + eng)

        newfra = input("Trad=") or voc[1]
        db.cursor.execute("UPDATE `voc` SET `fra`=%s, `difficulteJP`=0 WHERE `id`=%s", (newfra, voc[0]))
        db.conn.commit()

        remove_id_from_errors()
        print()
