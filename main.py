from tkinter import *
from src.GUI import windows
from src.config import Config

# объект Config должен быть создан только 1 раз !
cfg = Config()

app = Tk()
windows.KeyCheckerWindow(app, cfg.key_checker)
app.mainloop()

app = Tk()
windows.MainWindow(app, cfg.main)
app.mainloop()
