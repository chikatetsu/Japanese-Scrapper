import colorama
from utils.bdd_class import ConnectionDatabase


### Get the max length of an element in the database

colorama.init()
db = ConnectionDatabase()

max = 0
db.cursor.execute("SELECT `jap`, `url` FROM `voc`")
res = db.cursor.fetchall()
for r in res:
    if r[0] is None:
        continue
    if len(r[0]) > max:
        max = len(r[0])
print(max)

# for r in res:
#     if r[0] is None:
#         continue
#     if len(r[0]) != max:
#         continue
#     print(r[0], r[1])
#     with open("save/same_url.txt", "a", encoding="utf-8") as f:
#         f.write(r[1]+"\n")




# with open("save/phrase.txt", "r", encoding="utf-8") as f:
#     links = f.read()
# links = links.split("\n")
#
# max = 100
# for l in links:
#     if len(l) < max:
#         continue
#     db.cursor.execute("SELECT `id` FROM `voc` WHERE `url`=%s", (l[:100],))
#     res = db.cursor.fetchall()
#     if len(res) == 0:
#         continue
#     if len(res) > 1:
#         print(colorama.Fore.YELLOW, "plusieurs résultats pour :\n", l, colorama.Fore.RESET)
#         with open("save/same_url.txt", "a", encoding="utf-8") as f:
#             f.write(l+"\n")
#     else:
#         print(res[0][0])
#         db.cursor.execute("UPDATE `voc` SET `url`=%s WHERE `id`=%s", (l, res[0][0]))
#         db.conn.commit()
