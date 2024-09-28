# requirements.txt
# pymupdf
from   tkinter     import *
from   tkinter     import ttk
from   tkinter     import filedialog
from   PIL         import ImageTk, Image
import os
import pymupdf
import io


buffer = []
images = []
pdfs   = []
currow = 1


root      = Tk()
root.title("Assemble PDF")
canvas    = Canvas(root, borderwidth=0)
frame     = ttk.Frame(canvas)
scrollbar = ttk.Scrollbar(
              root,
              orient="vertical",
              command=canvas.yview
            )
canvas.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)


def update_scrollregion():
  canvas.configure(scrollregion=canvas.bbox("all"))


frame.bind("<Configure>", lambda _: update_scrollregion())
canvas.create_window((19,4), window=frame, anchor="nw")
parent = frame

def add_element(element):
  element.pack()


def reload_frame():
  for child in parent.winfo_children():
    child.destroy()
  button = ttk.Button(parent, text="+", command=open_file)
  add_element(button)
  for img in images:
    load_image(img)


def load_image(img):
  width, height = img.size
  width         = int(300 * width / height)
  height        = 300
  img           = img.resize((width,height))
  imgtk         = ImageTk.PhotoImage(img)
  panel         = ttk.Label(parent, image=imgtk)
  panel.image   = imgtk
  add_element(panel)


def load_fimage(filename):
  img         = Image.open(filename).resize((300,300))
  img.resize((100,100))
  imgtk       = ImageTk.PhotoImage(img)
  panel       = ttk.Label(win, image=imgtk)
  panel.image = imgtk
  add_element(panel)


def pdf2img(filename):
  img = []
  for page in pymupdf.open(filename):
    pixmap = page.get_pixmap()
    buffer.append(io.BytesIO(pixmap.tobytes()))
    img.append(Image.open(buffer[-1]))
  return img


def open_file():
  global images
  filename = filedialog.askopenfilename(
    title="Open file",
    initialdir=os.path.dirname(os.path.realpath(__file__)),
    filetypes=[("All files", "*.*")]
  )
  _, extension = os.path.splitext(filename)
  if extension == ".pdf":
    images = images + pdf2img(filename)
  elif extension == ".jpg" \
  or   extension == ".jpeg" \
  or   extension == ".png" \
  or   extension == ".gif" \
  or   extension == ".bmp":
    ttk.Label(parent, text=f"Image! {extension}").pack()
  else:
    ttk.Label(parent, text=f"Garbage! {extension}").pack()
  reload_frame()


reload_frame()
# button = ttk.Button(parent, text="+", command=open_file)
# button.pack()

root.mainloop()
