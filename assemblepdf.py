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


buffer  = []
images  = []
pdfs    = []
currow  = 1
wcanvas = 800
hcanvas = 600
himages = 300
maxw    = 100

root      = Tk()
root.title("Assemble PDF")
canvas    = Canvas(root, width=wcanvas, height=hcanvas)
frame     = ttk.Frame(canvas)
scrollbar = ttk.Scrollbar(
              root,
              orient="vertical",
              command=canvas.yview
            )
canvas.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)


def update_scrollregion(*args):
  canvas.configure(scrollregion=canvas.bbox("all"))


frame.bind("<Configure>", update_scrollregion)
canvas.create_window((int((wcanvas - 640) / 2),0), window=frame, anchor="nw")
parent = frame


def add_element(element):
  element.pack()


def reload_frame():
  global canvas
  global frame
  canvas.delete("all")
  for child in parent.winfo_children():
    child.destroy()
  button_frame  = ttk.Frame(parent)
  add_element(button_frame)
  add_element(ttk.Button(button_frame, text="+", command=open_file))
  add_element(ttk.Button(button_frame, text="Export", command=export))
  for img in images:
    load_image(img)
  canvas.create_window((int((wcanvas - maxw) / 2),0), window=frame, anchor="nw")


def load_image(img):
  global maxw
  width, height = img.size
  width         = int(300 * width / height)
  height        = 300
  if width > maxw:
    maxw = width
  img           = img.resize((width,height))
  imgtk         = ImageTk.PhotoImage(img)
  panel         = ttk.Label(parent, image=imgtk)
  panel.image   = imgtk
  add_element(panel)


def load_fimage(filename):
  img = Image.open(filename)
  load_image(img)


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
    img        = Image.open(filename)
    wimg, himg = img.size
    doc        = pymupdf.Document()
    doc.new_page(pno=-1, width=wimg, height=himg)
    rect       = pymupdf.Rect(0, 0, wimg, himg)
    page = doc.load_page(0)
    page.insert_image(rect, filename=filename)
    images.append(img)
    pdfs.append(doc)
  else:
    ttk.Label(parent, text=f"Garbage! {extension}").pack()
  reload_frame()


def export(*args):
  filename = filedialog.asksaveasfilename()
  doc      = pymupdf.Document()
  for page in pdfs:
    doc.insert_pdf(page)
  doc.save(filename)

reload_frame()

root.mainloop()
