import threading
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
import os
import tkinter as tk
from PIL import Image, ImageTk



def get_text_from_image(img_path):
    if not img_path.endswith(".png") and not img_path.endswith(".jpg"):
        return ""
    image = Image.open(img_path)
    return pytesseract.image_to_string(image, lang='jpn')


def display_img(img_path):
    if not img_path.endswith(".png") and not img_path.endswith(".jpg"):
        return
    image = Image.open(img_path)

    image.thumbnail((750, 750))

    fenetre = tk.Tk()
    fenetre.title(img_path.split("/")[-1])
    photo = ImageTk.PhotoImage(image)

    label_image = tk.Label(fenetre, image=photo)
    label_image.pack()

    fenetre.mainloop()


def ask_text(current_txt):
    print(current_txt)
    new_txt = input("correct text:")
    if new_txt != "":
        current_txt = new_txt
    with open(pdf_path + "all_text.txt", "a", encoding="utf-8") as f:
        f.write(current_txt + "\n")
    return current_txt


def get_all_text(path):
    global pdf_path
    if not os.path.exists(path):
        os.makedirs(path)
    txt = ""

    for filename in os.listdir(path):
        fullpath = os.path.join(path, filename)
        if os.path.isdir(fullpath):
            txt += get_all_text(fullpath)
            continue
        txt = get_text_from_image(fullpath)
        txt = txt.replace("\n", "")
        txt = txt.replace(" ", "")
        if txt == "":
            continue

        t1 = threading.Thread(target=display_img, args=(fullpath,))
        t2 = threading.Thread(target=ask_text, args=(txt,))
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        os.remove(fullpath)
        print()


if __name__ == "__main__":
    pdf_path = "C:/Users/kakap/Desktop/JAP_Sentences/pngs/"
    get_all_text(pdf_path)
