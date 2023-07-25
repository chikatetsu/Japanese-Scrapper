import os


def generate_batch(folder_path):
    for filename in os.listdir(folder_path):
        if not filename.endswith(".py"):
            continue
        with open(filename.replace(".py", ".bat"), "w", encoding="utf-8") as f:
            f.write("cd " + folder_path + "\n")
            f.write("python " + filename + "\n")
            f.write("if %errorlevel% NEQ 0 (\n")
            f.write("\techo 'Une erreur est survenue'\n")
            f.write("\tpause\n")
            f.write(")\n")


# Delete all batchs in the folder
batchs = os.listdir(".")
for batch in batchs:
    if not batch.endswith(".bat"):
        continue
    os.remove(batch)


folder_path = "../"
generate_batch(folder_path)
