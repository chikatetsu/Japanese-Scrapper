from utils.bdd_class import ConnectionDatabase


if __name__ == '__main__':
    db = ConnectionDatabase()


    with open("save/kanjiless.txt", "r", encoding="utf-8") as f:
        words = f.read().split("\n")


    for w in words:
        w = w.split("\t")
        print(w[0] + " at " + w[1])

        db.cursor.execute("SELECT `kana` FROM `voc` WHERE `id`=%s", (int(w[0]),))
        kana = db.cursor.fetchone()[0]
        if kana == "" or kana is None:
            print("Kana is NULL")
            break

        db.cursor.execute("UPDATE `voc` SET `jap`=`kana`, `kana`=NULL, `difficulte`=NULL WHERE `id`=%s", (int(w[0]),))
    db.conn.commit()
    db.close()
