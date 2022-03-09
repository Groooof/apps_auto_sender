from tkinter import *
from tkinter.ttk import *
from enum import Enum


class Colors:
    def __init__(self):
        self.main = '#5CDB95'
        self.main_lighter = '#8EE4AF'
        self.text = '#05386B'
        self.text_lighter = '#EDF5E1'
        self.brr = '#379683'


class StylesSetter:
    def __init__(self):
        self.colors = Colors()
        self.style = Style()

    def set(self):
        self.style.theme_use('alt')
        self.style.configure('TButton', relief=FLAT, cursor="hand2")
        self.style.configure('TFrame', background=self.colors.main, foreground=self.colors.text)
        self.style.configure('Light.TFrame', background=self.colors.main_lighter, foreground=self.colors.text)
        self.style.configure('TEntry', fieldbackground=self.colors.text_lighter, foreground=self.colors.text)
        self.style.configure('TLabel', background=self.colors.main, foreground=self.colors.text)
        self.style.configure('Light.TLabel', background=self.colors.main_lighter, foreground=self.colors.text)
        self.style.configure('TLabelframe', background=self.colors.main_lighter, foreground=self.colors.text)
        self.style.configure('TLabelframe.Label', background=self.colors.main_lighter, foreground=self.colors.text)
        self.style.configure('Treeview.Heading', background=self.colors.main, foreground=self.colors.text)
        self.style.configure('Treeview', background=self.colors.text_lighter, fieldbackground=self.colors.text_lighter,
                             foreground=self.colors.text)

        self.style.map('TButton',
                       background=[('!active', self.colors.text),
                                   ('pressed', self.colors.text)],
                       foreground=[('!active', self.colors.text_lighter),
                                   ('pressed', self.colors.main)])

        self.style.map('Treeview.Heading',
                       background=[('!active', self.colors.main),
                                   ('pressed', self.colors.text)],
                       foreground=[('!active', self.colors.text),
                                   ('pressed', self.colors.main)])

