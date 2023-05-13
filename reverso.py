import time
import keyboard as keyboard
import pyautogui as pag
from utils.bdd_class import ConnectionDatabase
from utils.index_class import Index
import pyperclip


def change_onglet(i_voc):
    if i_voc % 2 == 0:
        pag.moveTo(136, 25)
    else:
        pag.moveTo(423, 25)
    pag.click()


def paste_word(i_voc):
    pag.moveTo(950, 376)
    pag.click()
    pyperclip.copy(voc[i_voc][1])
    pag.moveTo(500, 420)
    pag.click()
    pag.hotkey('ctrl', 'v')



def on_shift_press(event):
    if keyboard.is_pressed('shift'):
        global end_program
        end_program = True
        print("shift pressed")



if __name__ == '__main__':
    end_program = False
    keyboard.on_press(on_shift_press)

    db = ConnectionDatabase()

    db.cursor.execute("SELECT `id`, `fra` FROM `voc` ORDER BY `id`")
    voc = db.cursor.fetchall()

    index = Index("save/processReverso.txt")
    time.sleep(5)

    while index.value < len(voc) and not end_program:
        # input word in 1st onglet
        change_onglet(index.value)
        paste_word(index.value)

        # input word in 2nd onglet
        change_onglet(index.value + 1)
        paste_word(index.value + 1)

        ### onglet 1 | 2
        # get result
        # paste word
        for i in range(index.value + 2, len(voc)):
            change_onglet(i)

            time.sleep(2)
            if end_program:
                break
            pag.moveTo(1016, 398)
            for j in range(3):
                pag.click()
            pyperclip.copy("")
            pag.hotkey('ctrl', 'c')
            print(voc[i-2][0], "\t", pyperclip.paste())
            if pyperclip.paste() == "":
                print("Temps épuisé")
                break
            db.cursor.execute("UPDATE `voc` SET `fra`=%s WHERE `id`=%s", (pyperclip.paste(), voc[i-2][0]))
            db.conn.commit()

            index.value = i - 1
            index.save()
            paste_word(i)

    db.close()