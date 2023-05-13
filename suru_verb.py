import colorama
from utils.bdd_class import ConnectionDatabase



if __name__ == '__main__':
    colorama.init()
    db = ConnectionDatabase()

    db.cursor.execute("SELECT `id`, `jap` FROM `voc` WHERE `id` IN (SELECT `idVoc` FROM `categoriesvoc` WHERE `idCategorie`=2)")
    suru_verb = db.cursor.fetchall()

    for sv in suru_verb:
        if sv[1].endswith("する") :
            continue

        db.cursor.execute("SELECT * FROM `categoriesvoc` WHERE `idVoc`=%s", (sv[0],))
        cats = db.cursor.fetchall()
        if len(cats) > 1:
            # TODO
            continue

        db.cursor.execute("UPDATE `voc` SET `jap`=%s WHERE `id`=%s", (sv[1]+"する", sv[0]))
        db.conn.commit()



# suru verb deja enregistré
    # ne rien faire

# suru verb non enregistrés
    # suru à la fin
        # ne rien faire

    # pas suru à la fin
        # juste 1 categorie
            # modifier le mot avec suru à la fin

        # plusieurs catégories
            # ajouter un mot
            # ajouter suru à ce mot
            # enlever suru sur l'ancien mot
