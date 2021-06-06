from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
import os
import numpy as np
import pydicom as pd
from PIL import Image, ImageTk
from scipy import ndimage
import cv2.cv2 as cv2

# CARATTERISTICHE
# viste di tomografie su tre piani
# zoom
# segmentazione manuale

######################################## lETTURA E PREPARAZIONE DATI ########################################

# inizializzazione tkinter interpreter, attribuzione di titolo e geometria della finestra root
root = Tk()
root.title('DICOM visualizer')
#root.attributes('-fullscreen', True)

# scelta directory contenente le tomografie tramite finestra di dialogo e
# creazione lista dei path di tutte i file .dcm presenti nella directory
slices = []
slice0 = ()
directory = []
answer = 1
while answer == 1:
    directory = filedialog.askdirectory(master=root, initialdir='C:/')
    for dirName, subdirList, fileList in os.walk(directory):
        for file in fileList:
            if file.endswith('.dcm'):
                slices.append(os.path.join(dirName, file))
    answer = 0
    # verifica di aver selezionato una cartella contenente file .dcm
    try:
        slice0 = pd.dcmread(slices[0])
    except IndexError:
        answer = messagebox.askyesno(master=root, message='File not found.\nWant to retry?')

try:
    slice0 = pd.dcmread(slices[0])
except IndexError:
    quit()

# estrazione tag
dimensions = (slice0.Rows, slice0.Columns, len(slices), 2)
date = slice0.get('StudyDate', 'NA')
# inizializzazione array 3d
dicom_array = np.zeros(dimensions)

# popolazione array 3d
for i in slices:
    axl_img_1 = pd.dcmread(i)
    axl_img_1to2 = cv2.normalize(axl_img_1.pixel_array, None, 255, 0, cv2.NORM_MINMAX)

    # merge di due array per risolvere problemi di visualizzazione dell'array mascherato
    axl_img_2 = cv2.merge([axl_img_1to2, axl_img_1to2])
    dicom_array[:, :, slices.index(i), :] = axl_img_2

# inizializzazione mask e creazione array mascherato
mask = np.ma.empty_like(dicom_array)
masked_dicom = np.ma.masked_array(dicom_array, mask)

################################################## WIDGET PER I TAG ##################################################

# creazione di label e entry con i valori estratti dai tag dei file .dcm
no_l = Label(root, text='\n\n\n\n\n')
no_l.grid(row=0, column=0)

path_l = Label(root, text='Path:')
path_l.grid(row=1, column=0)

entry_path = Entry(root, width=49)
entry_path.insert(0, directory)
entry_path.grid(row=1, column=1)

dims_l = Label(root, text='Dimensions:')
dims_l.grid(row=2, column=0)

entry_dims = Entry(root, width=49)
entry_dims.insert(0, str(dimensions[0]) + 'x' + str(dimensions[1]) + 'x' + str(dimensions[2]))
entry_dims.grid(row=2, column=1)

mod_l = Label(root, text='Modality:')
mod_l.grid(row=3, column=0)

entry_mod = Entry(root, width=49)
entry_mod.insert(0, slice0.get('Modality', 'NA'))
entry_mod.grid(row=3, column=1)

date_l = Label(root, text='Date:')
date_l.grid(row=4, column=0)

entry_date = Entry(root, width=49)
entry_date.insert(0, date[0:4] + '/' + date[4:6] + '/' + date[6:8])
entry_date.grid(row=4, column=1)

des_l = Label(root, text='Description:')
des_l.grid(row=5, column=0)

entry_des = Entry(root, width=49)
entry_des.insert(0, slice0.get('SeriesDescription', 'NA'))
entry_des.grid(row=5, column=1)

######################################## WIDGET PER LA VISUALIZZAZIONE ########################################

#-------------------------------------------------- PIANO CORONALE --------------------------------------------------#
# inizializzazione widget
des_l = Label(root, text='CORONAL TOMOGRAPHIES:')
des_l.grid(row=0, column=2, columnspan=5)

# l'immagine viene interpolata lungo l'asse orizzontale per raggiungere le stesse dimensioni della tomografia assiale
# e poi viene mostrata sul canvas
canvas_crn = Canvas(root, width=dimensions[0], height=dimensions[1], bg='gray')
canvas_crn.grid(row=1, column=2, rowspan=8, columnspan=5)
ca1 = ImageTk.PhotoImage(image=Image.fromarray(masked_dicom[0, :, :, 1]).resize((dimensions[0], dimensions[1]),
                                                                                Image.LANCZOS))
canvas_crn.create_image(257, 257, anchor='c', image=ca1)

# slider tomografie


def slide_crn(val):
    global ca1

    # mostra la sezione coronale del valore indicato dallo slider
    canvas_crn.delete(ca1)
    ca1 = ImageTk.PhotoImage(image=Image.fromarray(masked_dicom[int(val)-1, :, :, 1]).resize(
        (dimensions[0], dimensions[1]), Image.LANCZOS))
    canvas_crn.create_image(257, 257, anchor='c', image=ca1)


slider_crn = Scale(root, from_=1, to=dimensions[0], length=450, orient=HORIZONTAL, command=slide_crn)
slider_crn.grid(row=9, column=2, columnspan=5)

# funzione per la segmentazione manuale


def paint_crn(event):
    global ca, ca1, ca2
    global masked_dicom

    # definisco gli estremi in orizzontale e verticale del quadrato di pixel selezionato usando il mouse
    x1, y1, x2, y2 = (event.x - 2), (event.y - 2), (event.x + 2), (event.y + 2)

    # per ogni pixel interno agli estremi del quadrato, si pone =1 il corrispondente elemento di mask
    for j in range(x1, x2):
        for k in range(y1, y2):
            if j in range(dimensions[0]) and k in range(dimensions[1]):
                mask[slider_crn.get()-1, k, round(j*int(dimensions[2])/dimensions[1]), 1] = 1

    # si mostrano le nuove immagini ottenute mascherando il dicom_array
    canvas_axl.delete(ca)
    canvas_axl.delete(ca1)
    canvas_axl.delete(ca2)
    masked_dicom = np.ma.masked_array(dicom_array, mask, fill_value=255)
    ca = ImageTk.PhotoImage(image=Image.fromarray(masked_dicom[:, :, slider_axl.get()-1, 1]))
    canvas_axl.create_image(257, 257, anchor='c', image=ca)
    ca1 = ImageTk.PhotoImage(image=Image.fromarray(masked_dicom[slider_crn.get()-1, :, :, 1]).resize(
        (dimensions[0], dimensions[1]), Image.LANCZOS))
    canvas_crn.create_image(257, 257, anchor='c', image=ca1)
    ca2 = ImageTk.PhotoImage(image=Image.fromarray(masked_dicom[:, slider_sgt.get()-1, :, 1]).resize(
        (dimensions[0], dimensions[1]), Image.LANCZOS))
    canvas_sgt.create_image(257, 257, anchor='c', image=ca2)


canvas_crn.bind('<B1-Motion>', paint_crn)

# funzione zoom
dx_crn = 0
dy_crn = 0
img_zoom_c = []


def zoom_crn(val):
    global ca1
    global img_zoom_c
    global dx_crn, dy_crn
    global slider_crn

    # se il valore è 1, l'immagine è a grandezza naturale e il widget per cambiare immagine è attivo
    if int(val) == 1:
        dx_crn = 0
        dy_crn = 0
        slider_crn.config(state=NORMAL, takefocus=0)
        canvas_crn.delete(img_zoom_c)
        slide_crn(slider_crn.get())

    # se il valore è superiore a 1, l'immagine viene ingrandita del valore selezionato e il widget per cambiare
    # immagine viene disattivo
    else:
        slider_crn.config(state=DISABLED, takefocus=0)
        if dx_crn > int(val)+2:
            dx_crn = int(val)+2
        elif dx_crn < -(int(val)+2):
            dx_crn = -(int(val)+2)
        if dy_crn > int(val)+2:
            dy_crn = int(val)+2
        elif dy_crn < -(int(val)+2):
            dy_crn = -(int(val)+2)
        resized = ndimage.zoom(masked_dicom[slider_crn.get()-1, :, :, 1], int(val))
        canvas_crn.delete(ca1)
        ca1 = ImageTk.PhotoImage(image=Image.fromarray(resized).resize(
            (dimensions[0]*int(val), dimensions[1]*int(val)), Image.LANCZOS))
        img_zoom_c = canvas_crn.create_image((257+(32*int(val)*dx_crn)), (257+(32*int(val)*dy_crn)), anchor='c',
                                             image=ca1)


slide_zoom_crn = Scale(root, from_=4, to=1, command=zoom_crn)
slide_zoom_crn.grid(row=10, column=2, rowspan=2)

#funzioni per muoversi sull'immagine zoomata


def left_crn():
    global img_zoom_c
    global dx_crn

    # è possibile muovere l'immagine solo se essa è stata zoomata e se non sono superati i bordi dell'immagine
    if slide_zoom_crn.get() != 1 and dx_crn < (slide_zoom_crn.get()+2):
        x = 32*slide_zoom_crn.get()
        dx_crn = dx_crn + 1
        y = 0
        canvas_crn.move(img_zoom_c, x, y)


def right_crn():
    global img_zoom_c
    global dx_crn
    if slide_zoom_crn.get() != 1 and dx_crn > -(slide_zoom_crn.get()+2):
        x = -32*slide_zoom_crn.get()
        dx_crn = dx_crn - 1
        y = 0
        canvas_crn.move(img_zoom_c, x, y)


def up_crn():
    global img_zoom_c
    global dy_crn
    if slide_zoom_crn.get() != 1 and dy_crn < (slide_zoom_crn.get()+2):
        x = 0
        y = 32*slide_zoom_crn.get()
        dy_crn = dy_crn + 1
        canvas_crn.move(img_zoom_c, x, y)


def down_crn():
    global img_zoom_c
    global dy_crn
    if slide_zoom_crn.get() != 1 and dy_crn > -(slide_zoom_crn.get()+2):
        x = 0
        y = -32*slide_zoom_crn.get()
        dy_crn = dy_crn - 1
        canvas_crn.move(img_zoom_c, x, y)


left_b_crn = Button(root, width=10, height=10, text='<', command=left_crn)
left_b_crn.grid(row=10, column=3, rowspan=2)

right_b_crn = Button(root, width=10, height=10, text='>', command=right_crn)
right_b_crn.grid(row=10, column=6, rowspan=2)

up_b_crn = Button(root, width=25, height=5, text='^', command=up_crn)
up_b_crn.grid(row=10, column=4, columnspan=2)

down_b_crn = Button(root, width=25, height=5, text='v', command=down_crn)
down_b_crn.grid(row=11, column=4, columnspan=2)


#-------------------------------------------------- PIANO SAGITTALE --------------------------------------------------#
# inizializzazione widget
des_l = Label(root, text='SAGITTAL TOMOGRAPHIES:')
des_l.grid(row=0, column=12, columnspan=5)

canvas_sgt = Canvas(root, width=dimensions[0], height=dimensions[1], bg='gray')
canvas_sgt.grid(row=1, column=12, rowspan=8, columnspan=5)
ca2 = ImageTk.PhotoImage(image=Image.fromarray(masked_dicom[:, 0, :, 1]).resize((dimensions[0], dimensions[1]),
                                                                                Image.LANCZOS))
canvas_sgt.create_image(257, 257, anchor='c', image=ca2)

# slider tomografie


def slide_sgt(val):
    global ca2
    canvas_sgt.delete(ca2)
    ca2 = ImageTk.PhotoImage(image=Image.fromarray(masked_dicom[:, int(val)-1, :, 1]).resize(
        (dimensions[0], dimensions[1]), Image.LANCZOS))
    canvas_sgt.create_image(257, 257, anchor='c', image=ca2)


slider_sgt = Scale(root, from_=1, to=dimensions[1], length=450, orient=HORIZONTAL, command=slide_sgt)
slider_sgt.grid(row=9, column=12, columnspan=5)


# funzione per la segmentazione manuale


def paint_sgt(event):
    global ca, ca1, ca2
    global masked_dicom
    x1, y1, x2, y2 = (event.x - 2), (event.y - 2), (event.x + 2), (event.y + 2)
    for j in range(x1, x2):
        for k in range(y1, y2):
            if j in range(dimensions[0]) and k in range(dimensions[1]):
                mask[k, slider_sgt.get()-1, round(j*int(dimensions[2])/dimensions[0]), 1] = 1
    canvas_axl.delete(ca)
    canvas_axl.delete(ca1)
    canvas_axl.delete(ca2)
    masked_dicom = np.ma.masked_array(dicom_array, mask, fill_value=255)
    ca = ImageTk.PhotoImage(image=Image.fromarray(masked_dicom[:, :, slider_axl.get()-1, 1]))
    canvas_axl.create_image(257, 257, anchor='c', image=ca)
    ca1 = ImageTk.PhotoImage(image=Image.fromarray(masked_dicom[slider_crn.get()-1, :, :, 1]).resize(
        (dimensions[0], dimensions[1]), Image.LANCZOS))
    canvas_crn.create_image(257, 257, anchor='c', image=ca1)
    ca2 = ImageTk.PhotoImage(image=Image.fromarray(masked_dicom[:, slider_sgt.get()-1, :, 1]).resize(
        (dimensions[0], dimensions[1]), Image.LANCZOS))
    canvas_sgt.create_image(257, 257, anchor='c', image=ca2)


canvas_sgt.bind('<B1-Motion>', paint_sgt)


# funzione zoom
dx_sgt = 0
dy_sgt = 0
img_zoom_s = []


def zoom_sgt(val):
    global ca2
    global img_zoom_s
    global dx_sgt, dy_sgt
    global slider_sgt
    if int(val) == 1:
        dx_sgt = 0
        dy_sgt = 0
        slider_sgt.config(state=NORMAL, takefocus=0)
        canvas_sgt.delete(img_zoom_s)
        slide_sgt(slider_sgt.get())
    else:
        slider_sgt.config(state=DISABLED, takefocus=0)
        if dx_sgt > int(val)+2:
            dx_sgt = int(val)+2
        elif dx_sgt < -(int(val)+2):
            dx_sgt = -(int(val)+2)
        if dy_sgt > int(val)+2:
            dy_sgt = int(val)+2
        elif dy_sgt < -(int(val)+2):
            dy_sgt = -(int(val)+2)
        resized = ndimage.zoom(masked_dicom[:, slider_sgt.get()-1, :, 1], int(val))
        canvas_sgt.delete(ca2)
        ca2 = ImageTk.PhotoImage(image=Image.fromarray(resized).resize(
            (dimensions[0]*int(val), dimensions[1]*int(val)), Image.LANCZOS))
        img_zoom_s = canvas_sgt.create_image((257+(32*int(val)*dx_sgt)), (257+(32*int(val)*dy_sgt)), anchor='c',
                                             image=ca2)


slide_zoom_sgt = Scale(root, from_=4, to=1, command=zoom_sgt)
slide_zoom_sgt.grid(row=10, column=12, rowspan=2)

#funzioni per muoversi sull'immagine zoomata


def left_sgt():
    global img_zoom_s
    global dx_sgt
    if slide_zoom_sgt.get() != 1 and dx_sgt < (slide_zoom_sgt.get()+2):
        x = 32*slide_zoom_sgt.get()
        dx_sgt = dx_sgt + 1
        y = 0
        canvas_sgt.move(img_zoom_s, x, y)


def right_sgt():
    global img_zoom_s
    global dx_sgt
    if slide_zoom_sgt.get() != 1 and dx_sgt > -(slide_zoom_sgt.get()+2):
        x = -32*slide_zoom_sgt.get()
        dx_sgt = dx_sgt - 1
        y = 0
        canvas_sgt.move(img_zoom_s, x, y)


def up_sgt():
    global img_zoom_s
    global dy_sgt
    if slide_zoom_sgt.get() != 1 and dy_sgt < (slide_zoom_sgt.get()+2):
        x = 0
        y = 32*slide_zoom_sgt.get()
        dy_sgt = dy_sgt + 1
        canvas_sgt.move(img_zoom_s, x, y)


def down_sgt():
    global img_zoom_s
    global dy_sgt
    if slide_zoom_sgt.get() != 1 and dy_sgt > -(slide_zoom_sgt.get()+2):
        x = 0
        y = -32*slide_zoom_sgt.get()
        dy_sgt = dy_sgt - 1
        canvas_sgt.move(img_zoom_s, x, y)


right_b_sgt = Button(root, width=10, height=10, text='>', command=right_sgt)
right_b_sgt.grid(row=10, column=16, rowspan=2)

left_b_sgt = Button(root, width=10, height=10, text='<', command=left_sgt)
left_b_sgt.grid(row=10, column=13, rowspan=2)

up_b_sgt = Button(root, width=25, height=5, text='^', command=up_sgt)
up_b_sgt.grid(row=10, column=14, columnspan=2)

down_b_sgt = Button(root, width=25, height=5, text='v', command=down_sgt)
down_b_sgt.grid(row=11, column=14, columnspan=2)

#-------------------------------------------------- PIANO ASSIALE --------------------------------------------------#
# inizializzazione widget
des_l = Label(root, text='AXIAL TOMOGRAPHIES:')
des_l.grid(row=0, column=7, columnspan=5)

canvas_axl = Canvas(root, width=dimensions[0], height=dimensions[1], bg='gray')
canvas_axl.grid(row=1, column=7, rowspan=8, columnspan=5)
ca = ImageTk.PhotoImage(image=Image.fromarray(masked_dicom[:, :, 0, 1]))
canvas_axl.create_image(257, 257, anchor='c', image=ca)

# slider tomografie


def slide_axl(val):
    global ca
    global masked_dicom
    canvas_axl.delete(ca)
    ca = ImageTk.PhotoImage(image=Image.fromarray(masked_dicom[:, :, int(val)-1, 1]))
    canvas_axl.create_image(257, 257, anchor='c', image=ca)


slider_axl = Scale(root, from_=1, to=dimensions[2], length=450, orient=HORIZONTAL, command=slide_axl)
slider_axl.grid(row=9, column=7, columnspan=5)

# funzione per la segmentazione manuale


def paint_axl(event):
    global ca, ca1, ca2
    global masked_dicom
    x1, y1, x2, y2 = (event.x - 2), (event.y - 2), (event.x + 2), (event.y + 2)
    for j in range(x1, x2):
        for k in range(y1, y2):
            if j in range(dimensions[1]) and k in range(dimensions[0]):
                mask[k, j, slider_axl.get()-1, 1] = 1
    canvas_axl.delete(ca)
    canvas_axl.delete(ca1)
    canvas_axl.delete(ca2)
    masked_dicom = np.ma.masked_array(dicom_array, mask, fill_value=255)
    ca = ImageTk.PhotoImage(image=Image.fromarray(masked_dicom[:, :, slider_axl.get()-1, 1]))
    canvas_axl.create_image(257, 257, anchor='c', image=ca)
    ca1 = ImageTk.PhotoImage(image=Image.fromarray(masked_dicom[slider_crn.get()-1, :, :, 1]).resize(
            (dimensions[0], dimensions[1]), Image.LANCZOS))
    canvas_crn.create_image(257, 257, anchor='c', image=ca1)
    ca2 = ImageTk.PhotoImage(image=Image.fromarray(masked_dicom[:, slider_sgt.get()-1, :, 1]).resize(
            (dimensions[0], dimensions[1]), Image.LANCZOS))
    canvas_sgt.create_image(257, 257, anchor='c', image=ca2)


canvas_axl.bind('<B1-Motion>', paint_axl)

# funzione zoom
dx_axl = 0
dy_axl = 0
img_zoom_a = []


def zoom_axl(val):
    global ca
    global masked_dicom
    global img_zoom_a
    global dx_axl, dy_axl
    global slider_axl
    if int(val) == 1:
        dx_axl = 0
        dy_axl = 0
        slider_axl.config(state=NORMAL, takefocus=0)
        canvas_axl.delete(img_zoom_a)
        slide_axl(slider_axl.get())
    else:
        slider_axl.config(state=DISABLED, takefocus=0)
        if dx_axl > int(val)+2:
            dx_axl = int(val)+2
        elif dx_axl < -(int(val)+2):
            dx_axl = -(int(val)+2)
        if dy_axl > int(val)+2:
            dy_axl = int(val)+2
        elif dy_axl < -(int(val)+2):
            dy_axl = -(int(val)+2)
        resized = ndimage.zoom(masked_dicom[:, :, slider_axl.get()-1, 1], int(val))
        canvas_axl.delete(ca)
        ca = ImageTk.PhotoImage(image=Image.fromarray(resized))
        img_zoom_a = canvas_axl.create_image((257+(32*int(val)*dx_axl)), (257+(32*int(val)*dy_axl)), anchor='c',
                                             image=ca)


slide_zoom_axl = Scale(root, from_=4, to=1, command=zoom_axl)
slide_zoom_axl.grid(row=10, column=7, rowspan=2)

# funzioni per muoversi sull'immagine zoomata


def left_axl():
    global img_zoom_a
    global dx_axl
    if slide_zoom_axl.get() != 1 and dx_axl < (slide_zoom_axl.get()+2):
        x = 32*slide_zoom_axl.get()
        dx_axl = dx_axl+1
        y = 0
        canvas_axl.move(img_zoom_a, x, y)


def right_axl():
    global img_zoom_a
    global dx_axl
    if slide_zoom_axl.get() != 1 and dx_axl > -(slide_zoom_axl.get()+2):
        x = -32*slide_zoom_axl.get()
        dx_axl = dx_axl-1
        y = 0
        canvas_axl.move(img_zoom_a, x, y)


def up_axl():
    global img_zoom_a
    global dy_axl
    if slide_zoom_axl.get() != 1 and dy_axl < (slide_zoom_axl.get()+2):
        x = 0
        y = 32*slide_zoom_axl.get()
        dy_axl = dy_axl+1
        canvas_axl.move(img_zoom_a, x, y)


def down_axl():
    global img_zoom_a
    global dy_axl
    if slide_zoom_axl.get() != 1 and dy_axl > -(slide_zoom_axl.get()+2):
        x = 0
        y = -32*slide_zoom_axl.get()
        dy_axl = dy_axl - 1
        canvas_axl.move(img_zoom_a, x, y)


right_b_axl = Button(root, width=10, height=10, text='>', command=right_axl)
right_b_axl.grid(row=10, column=11, rowspan=2)

left_b_axl = Button(root, width=10, height=10, text='<', command=left_axl)
left_b_axl.grid(row=10, column=8, rowspan=2)

up_b_axl = Button(root, width=25, height=5, text='^', command=up_axl)
up_b_axl.grid(row=10, column=9, columnspan=2)

down_b_axl = Button(root, width=25, height=5, text='v', command=down_axl)
down_b_axl.grid(row=11, column=9, columnspan=2)

#---------------------------------------- ALTRE FUNZIONI ----------------------------------------#
# funzione per rimuovere la maschera


def clear_all():
    global mask
    global masked_dicom
    global ca, ca1, ca2
    mask = np.ma.empty_like(dicom_array)
    masked_dicom = np.ma.masked_array(dicom_array, mask)
    canvas_axl.delete(ca)
    ca = ImageTk.PhotoImage(image=Image.fromarray(masked_dicom[:, :, slider_axl.get()-1, 1]))
    canvas_axl.create_image(257, 257, anchor='c', image=ca)
    canvas_crn.delete(ca1)
    ca1 = ImageTk.PhotoImage(image=Image.fromarray(masked_dicom[slider_crn.get()-1, :, :, 1]).resize(
        (dimensions[0], dimensions[1]), Image.LANCZOS))
    canvas_crn.create_image(257, 257, anchor='c', image=ca1)
    canvas_sgt.delete(ca2)
    ca2 = ImageTk.PhotoImage(image=Image.fromarray(masked_dicom[:, slider_sgt.get()-1, :, 1]).resize(
        (dimensions[0], dimensions[1]), Image.LANCZOS))
    canvas_sgt.create_image(257, 257, anchor='c', image=ca2)


button_clear = Button(root, text='Clear All', command=clear_all)
button_clear.grid(row=10, column=1)

# funzione per chiudere il programma
button_quit = Button(root, text='Exit', command=root.quit)
button_quit.grid(row=20, column=1)

root.mainloop()

exit()
