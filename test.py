#!/usr/bin/env python

import Tkinter as tk
import ttk
import tkFont
from datetime import datetime
from PIL import Image, ImageTk
import socket
import weaved as wv
import network as nw
import numpy as np
import helper
from time import sleep, time
import tkMessageBox
import tkFileDialog
import tkSimpleDialog
import sys
import matplotlib.pyplot as plt
import pylab
from numpy import arange, sin, pi
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from difflib import SequenceMatcher as SM
from collections import Counter
from winsound import PlaySound as Play
from winsound import SND_FILENAME as sfn
import threading
from popup import WindowsBalloonTip
from idlelib.ToolTip import ToolTip as tip
#import animate
#import onsk


class Splash(tk.Toplevel):
    def __init__(self, parent):
        tk.Toplevel.__init__(self, parent)
        #splashscreen class
        self.title('HonuHome')
        self.attributes("-fullscreen", True)
        self.iconbitmap('./images/favicon.ico')
        self.configure(bg='#001F66')
        self.wm_attributes('-transparentcolor','#001F66')
        self.attributes('-alpha',0.90)
        self.overrideredirect(1)
        self.splash = ImageTk.PhotoImage(file='./images/splashscreen.png')
        tk.Label(self, image=self.splash, borderwidth=0, highlightthickness=0, bg='#646464').grid(row=0, column=0)
        self.rowconfigure(0, pad=124)
        self.columnconfigure(0, pad=704)
        self.update()


class App():
    def __init__(self):
        '''Initializes Honu Home main loop'''
        self.root = tk.Tk()
        self.root.attributes("-fullscreen", True)
        self.root.iconbitmap('./images/favicon.ico')
        self.root.withdraw()
        self.splash = Splash(self.root)
        #self.start_gui()
        self.Play = True
        self.shift = False
        self.root.deiconify()
        self.splash.destroy()
        #self.coverbg.focus_set()
        self.root.mainloop()


app=App()