import webbrowser
from utils.bdd_class import ConnectionDatabase

with open("save/error.txt", "r", encoding="utf-8") as f:
    txt = f.read()
txt = txt.split('\n')
db = ConnectionDatabase()

for i in range(len(txt)):
    db.cursor.execute("SELECT `id`,`fra`,`jap`,`kana` FROM `voc` WHERE `url`=%s", (txt[i],))
    voc = db.cursor.fetchall()

    print(voc)
    webbrowser.open("https://jisho.org/" + txt[i])
    if input("Supprimer? (o/n)") == "o":
        url_to_remove = txt[0]
        while url_to_remove in txt:
            txt.remove(url_to_remove)

        with open("save/error.txt", "w", encoding="utf-8") as f:
            f.write('\n'.join(txt))
    print()
