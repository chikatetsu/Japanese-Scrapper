import csv
import time

sql_file = 'save/from_csv.sql'
csv_file = 'save/voc(3).csv'

with open(sql_file, 'w', encoding='utf-8') as f:
    f.write('')

start = time.time()
with open(csv_file, encoding='utf-8') as c:
    csv_reader = csv.reader(c, delimiter='\t')
    for row in csv_reader:
        try:
            if start + 1 < time.time():
                start = time.time()
                print(row[0])
            with open(sql_file, 'a', encoding='utf-8') as f:
                f.write('UPDATE `voc` SET `fra`="' + str(row[1]) + '", `difficulteJP`=' + str(
                    row[2]) + ' WHERE `id`=' + str(row[0]) + ';\n')
        except:
            print("PROBLEME A CETTE LIGNE :\n", row)
            break
