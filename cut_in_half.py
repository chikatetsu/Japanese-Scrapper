filename = "save/from_csv(4)"
extension = ".sql"

with open(filename+extension, "r", encoding="utf-8") as f:
    lines = f.read().split('\n')
with open(filename+extension, "w", encoding="utf-8") as f:
    f.write('')

half = len(lines)/2
lenght = len(lines)
i = 0

with open(filename+"(1)"+extension, "a", encoding="utf-8") as f:
    while i < half:
        f.write(lines[i]+"\n")
        i += 1

with open(filename+"(2)"+extension, "a", encoding="utf-8") as f:
    while i < lenght:
        f.write(lines[i]+"\n")
        i += 1
