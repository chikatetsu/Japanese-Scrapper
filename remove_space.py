with open("save/allURL.txt", "r", encoding="utf-8") as f:
    links = list(map(str, f.read().split("\n")))

with open("save/newAllUrl.txt", "w", encoding="utf-8") as f:
    f.write("")

with open("save/newAllUrl.txt", "a", encoding="utf-8") as f:
    for l in links:
        f.write(l.replace("%20%23", "%23").replace("https://jisho.org/", "") + "\n")
