# requirements.txt
# pymupdf
import copy
from   tkinter     import *
from   tkinter     import ttk
from   tkinter     import filedialog
from   PIL         import ImageTk, Image
import os
import pymupdf
import io
import copy

buffer = []
images = []
pdfs   = []
maxw   = 0

root      = Tk()
root.title("PDF Builder")
wscreen   = root.winfo_screenwidth()
hscreen   = root.winfo_screenheight()
wcanvas   = int(wscreen / 2)
hcanvas   = int(hscreen / 2)
himages   = int(3 * hcanvas / 4)
cwbutton  = 20
button    = ttk.Button(root, width=cwbutton)
button.pack()
wbutton   = button.winfo_reqwidth()
button.destroy()
canvas    = Canvas(root, width=wcanvas, height=hcanvas)
mainframe = ttk.Frame(canvas)
scrollbar = ttk.Scrollbar(
              root,
              orient="vertical",
              command=canvas.yview
            )
canvas.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)


def update_canvas(*args):
  global wcanvas
  global hcanvas
  global wbutton
  wcanvas = canvas.winfo_width()
  hcanvas = canvas.winfo_height()
  canvas.delete("all")
  canvas.create_window((int((wcanvas - maxw) / 2 - wbutton),0), window=mainframe, anchor="nw")


canvas.bind("<Configure>", update_canvas)


def update_mainframe(*args):
  global canvas
  canvas.configure(scrollregion=canvas.bbox("all"))


mainframe.bind("<Configure>", update_mainframe)
# canvas.create_window((int((wcanvas - maxw - wbutton) / 2),0), window=mainframe, anchor="nw")
parent = mainframe


def add_element(element, side="top"):
  element.pack(side=side)


def page_up(number):
  if number == 0:
    return
  images[number], images[number - 1] = images[number - 1], images[number]
  pdfs[number], pdfs[number - 1] = pdfs[number - 1], pdfs[number]
  reload_mainframe()


def page_down(number):
  if number == len(images) - 1:
    return
  images[number], images[number + 1] = images[number + 1], images[number]
  pdfs[number], pdfs[number + 1] = pdfs[number + 1], pdfs[number]
  reload_mainframe()


def clockwise(number):
  page           = pdfs[number].load_page(0)
  page.set_rotation(page.rotation + 90)
  images[number] = images[number].transpose(Image.ROTATE_270)
  reload_mainframe()


def counterclockwise(number):
  page           = pdfs[number].load_page(0)
  page.set_rotation(page.rotation - 90)
  images[number] = images[number].transpose(Image.ROTATE_90)
  reload_mainframe()


def reload_mainframe():
  global canvas
  global mainframe
  global parent
  global maxw
  global wbutton
  canvas.delete("all")
  for child in parent.winfo_children():
    child.destroy()
  button_frame  = ttk.Frame(parent)
  button_frame.pack()
  ttk.Button(button_frame, text="Open File", command=open_file, width=cwbutton).pack(side="left")
  ttk.Button(button_frame, text="Export", command=export, width=cwbutton).pack(side="left")
  j = 0
  for img in images:
    img_frame     = ttk.Frame(parent)
    control_frame = ttk.Frame(img_frame)
    img_frame.pack()
    control_frame.pack(side="left")
    ttk.Button(control_frame, text="Clockwise", command=lambda number=j: clockwise(number), width=cwbutton).pack()
    ttk.Button(control_frame, text="Up", command=lambda number=j: page_up(number), width=cwbutton).pack()
    ttk.Button(control_frame, text="Down", command=lambda number=j: page_down(number), width=cwbutton).pack()
    ttk.Button(control_frame, text="Counterclockwise", command=lambda number=j: counterclockwise(number), width=cwbutton).pack()
    load_image(img, img_frame)
    j += 1
  # (wcanvas - (maxw + wbutton)) / 2
  # canvas.create_window((int((wcanvas - maxw - wbutton) / 2),0), window=mainframe, anchor="nw")
  canvas.create_window((int((wcanvas - maxw) / 2 - wbutton),0), window=mainframe, anchor="nw")


def load_image(img, parent):
  global maxw
  width, height = img.size
  width         = int(himages * width / height)
  height        = himages
  if width > maxw:
    maxw = width
  img           = img.resize((width,height))
  imgtk         = ImageTk.PhotoImage(img)
  panel         = ttk.Label(parent, image=imgtk)
  panel.image   = imgtk
  panel.pack()


def pdf2img(filename):
  img = []
  for page in pymupdf.open(filename):
    pixmap = page.get_pixmap()
    buffer.append(io.BytesIO(pixmap.tobytes()))
    img.append(Image.open(buffer[-1]))
    width, _ = img[-1].size
  return img


def split_pdf(filename):
  pages  = []
  tmp    = pymupdf.open(filename)
  doclen = tmp.page_count
  tmp.delete_pages(1, doclen - 1)
  pages.append(tmp)
  for j in range(1, doclen):
    tmp = pymupdf.open(filename)
    if j < doclen - 1:
      tmp.delete_pages(j + 1, doclen - 1)
    tmp.delete_pages(0, j - 1)
    pages.append(tmp)
  return pages


def img2pdf(fname):
    img        = Image.open(fname)
    wimg, himg = img.size
    doc        = pymupdf.Document()
    doc.new_page(pno=0, width=wimg, height=himg)
    rect       = pymupdf.Rect(0, 0, wimg, himg)
    page       = doc.load_page(0)
    page.insert_image(rect, filename=fname)
    return doc


def open_file():
  global images
  global pdfs
  filename = filedialog.askopenfilename(
    title="Open file",
    initialdir=os.path.dirname(os.path.realpath(__file__)),
    filetypes=[("All files", "*.*")]
  )
  _, extension = os.path.splitext(filename)
  if extension == ".pdf":
    images += pdf2img(filename)
    pdfs   += split_pdf(filename)
  elif extension == ".jpg" \
  or   extension == ".jpeg" \
  or   extension == ".png" \
  or   extension == ".gif" \
  or   extension == ".bmp":
    images.append(Image.open(filename))
    pdfs.append(img2pdf(filename))
  else:
    ttk.Label(parent, text=f"Garbage! {extension}").pack()
  reload_mainframe()


def export(*args):
  ext      = [("pdf", "*.pdf")]
  filename = filedialog.asksaveasfilename(filetypes=ext, defaultextension=ext)
  doc      = pymupdf.Document()
  for page in pdfs:
    doc.insert_pdf(page)
  doc.save(filename)

reload_mainframe()

root.mainloop()
