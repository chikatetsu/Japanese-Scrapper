import colorama

from utils.time_remaining import TimeRemaining
from utils.bdd_class import ConnectionDatabase

def trad_gare(word):
    word = word.replace(" Station", "")
    word = word.replace(" station", "")
    return "Gare de " + word


if __name__=="__main__":
    colorama.init()
    db = ConnectionDatabase()
    db.cursor.execute("SELECT `id`,`fra` FROM `voc` WHERE `fra` LIKE '%Station' AND (`difficulteJP`!=0 OR `difficulteJP` IS NULL) AND `id`>250000")
    stations = db.cursor.fetchall()
    tm = TimeRemaining(len(stations))

    reminder = 1
    for station in stations:
        tm.print_percent(stations.index(station))
        print(station[0], colorama.Fore.GREEN, station[1], colorama.Fore.RESET)
        response = input("Gare ou pas gare? (o/n/q) ")
        if response == "o":
            db.cursor.execute("UPDATE `voc` SET `fra`=%s, `difficulteJP`=0 WHERE `id`=%s", (trad_gare(station[1]), station[0]))
            db.cursor.execute("INSERT INTO `categoriesvoc`(`idVoc`, `idCategorie`) VALUES (%s, 22)", (station[0],))
        elif response == "q":
            break
        if reminder % 10 == 0:
            if input(colorama.Fore.RED + "Commit? (o/n) " + colorama.Fore.RESET) == "o":
                db.conn.commit()
        reminder += 1
        print()

    if input(colorama.Fore.RED + "Commit? (o/n) " + colorama.Fore.RESET) == "o":
        db.conn.commit()
    db.close()
