import webbrowser
from utils.bdd_class import ConnectionDatabase

with open("save/error.txt", "r", encoding="utf-8") as f:
    txt = f.read()
txt = txt.split('\n')
db = ConnectionDatabase()

for i in range(len(txt)):
    db.cursor.execute("SELECT `id`,`fra`,`jap`,`kana` FROM `voc` WHERE `url`=%s", (txt[i],))
    voc = db.cursor.fetchall()
    for v in voc:
        print(v)
    webbrowser.open("https://jisho.org/"+txt[i])
    if input("Supprimer? (o/n)") == "o":
        txt.pop(i)
        i -= 1
        with open("save/error.txt", "w", encoding="utf-8") as f:
            f.write('\n'.join(txt))
    print()
