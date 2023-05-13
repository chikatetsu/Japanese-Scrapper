import time

with open("save/allURL.txt", "r", encoding="utf-8") as f:
    links = list(map(str, f.read().split("\n")))
with open("save/example.txt", "w", encoding='utf-8') as f:
    f.write("")
with open("save/example_search.txt", "w", encoding='utf-8') as f:
    f.write("")
with open("save/kanji.txt", "w", encoding='utf-8') as f:
    f.write("")
with open("save/phrase.txt", "w", encoding='utf-8') as f:
    f.write("")
with open("save/forum.txt", "w", encoding="utf-8") as f:
    f.write("")
with open("save/reste.txt", "w", encoding="utf-8") as f:
    f.write("")

start = time.time()
old_value = 0
for l in links:
    if start < time.time():
        print((len(links) - links.index(l)) / (links.index(l) - old_value), "sec restantes")
        start = time.time()
        old_value = links.index(l)
    if l.startswith("forum"):
        with open("save/forum.txt", "a", encoding='utf-8') as f:
            f.write(l + "\n")
    elif l.startswith("word/"):
        with open("save/phrase.txt", "a", encoding='utf-8') as f:
            f.write(l + "\n")
    elif "%23sentences" in l:
        with open("save/example_search.txt", "a", encoding='utf-8') as f:
            f.write(l + "\n")
    elif l.startswith("sentences/"):
        with open("save/example.txt", "a", encoding='utf-8') as f:
            f.write(l + "\n")
    elif l.endswith("kanji"):
        with open("save/kanji.txt", "a", encoding='utf-8') as f:
            f.write(l + "\n")
    else:
        with open("save/reste.txt", "a", encoding='utf-8') as f:
            f.write(l + "\n")
