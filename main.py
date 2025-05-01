import tkinter as tk
from gui.app import App
from config.settings import ConfigFactory


if __name__ == "__main__":
    tk.Tk().withdraw()
    config = ConfigFactory.create_config()
    app = App(config)
    app.mainloop()