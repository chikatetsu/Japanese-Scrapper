import colorama
from utils.bdd_class import ConnectionDatabase


def save_bornes_norm():
    db.cursor.execute("SELECT MIN(`difficulte`) FROM `voc`")
    min = db.cursor.fetchone()[0]
    db.cursor.execute("SELECT MAX(`difficulte`) FROM `voc`")
    max = db.cursor.fetchone()[0]
    print(min, " ", max)
    with open("save/bornes_norm.txt", "w", encoding="utf-8") as f:
        f.write(str(min) + " " + str(max))


def get_bornes_norm():
    with open("save/bornes_norm.txt", "r", encoding="utf-8") as f:
        line = f.read()
    line = line.split(" ")
    return int(line[0]), int(line[1])



if __name__ == "__main__":
    colorama.init()
    db = ConnectionDatabase()

    db.cursor.execute("SELECT `id`, `difficulte` FROM `voc` WHERE `difficulte` < 0 OR `difficulte` > 1")
    not_normalized = db.cursor.fetchall()[0]

    min, max = get_bornes_norm()

    for diff in not_normalized:
        norm = (max - diff[1]) / (max - min)
        db.cursor.execute("UPDATE `voc` SET `difficulte`=%s WHERE `id`=%s", (norm, diff[0]))
        db.conn.commit()
    db.close()
