import tkinter as tk
from tkinter import ttk
import sys

from views.pages import Disclaimer, HomePage, MyPortfolio

class PersonalBroker(tk.Tk):

    def __init__(self, *args, **kwargs):
        
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.wm_title(self, 'Personal Broker')

        container = tk.Frame(self)
        container.pack(side='top', fill='both', expand=True)

        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)
        container.grid_rowconfigure(0, weight=1)

        self.frames = {}

        pages = [Disclaimer, HomePage, MyPortfolio]

        for page in pages:
            frame = page(container, self)
            self.frames[page] = frame
            frame.grid(column=0, row=0, columnspan=2, sticky='NESW')

        self.show_frame(Disclaimer)

    def show_frame(self, cont):

        frame = self.frames[cont]
        frame.tkraise()

app = PersonalBroker()
width = '1280'
height = '720'
screenWitdh = int((app.winfo_screenwidth() - int(width)) / 2)
screenHeight = int((app.winfo_screenheight() - int(height)) / 2)
posWidth = str(screenWitdh)
posHeight = str(screenHeight)
app.geometry(f'{width}x{height}+{posWidth}+{posHeight}')
app.mainloop()