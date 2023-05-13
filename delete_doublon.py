def save_links(filename):
    with open(filename, "w", encoding="utf-8") as f:
        f.write("")
    with open(filename, "a", encoding="utf-8") as f:
        for l in links:
            f.write(l + "\n")

with open("save/allURL.txt", "r", encoding="utf-8") as f:
    links = list(map(str, f.read().split("\n")))
with open("save/processDOUBLON.txt", "r", encoding="utf-8") as f:
    start = int(f.read())

save_links("save/safeAllURL.txt")
print("Nombre de liens à traiter :", len(links)-start)
print("Doublons :")

for i in range(start, len(links)):
    if links[i] in links[i+1:]:
        print(i, ":", links[i])
        links.remove(links[i])
        save_links("save/allURL.txt")
        print("Doublon supprimé")
    else:
        with open("save/processDOUBLON.txt", "w", encoding="utf-8") as f:
            f.write(str(i))
