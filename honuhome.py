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
import pandas as pd
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
        tk.Label(self, image=self.splash, borderwidth=0, highlightthickness=0, bg='#00a3fe').grid(row=0, column=0)
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
        self.start_gui()
        self.Play = True
        self.shift = False
        self.root.deiconify()
        self.splash.destroy()
        self.coverbg.focus_set()
        self.root.mainloop()


    def start_gui(self):
        '''Initialize Honu Home frames'''
        self.init_frames()
        self.init_styles()
        self.init_authentication_screen(self.fr1, True)
        self.init_cover()
        self.raise_frame(self.fr0)
        self.raise_frame(self.fra) #a
        self.init_ipscreen()
        self.init_anchor_select_screen()
        self.init_anchor_confirmation_screen()
        self.init_main_screen()
        self.init_control_screen()
        self.init_analytics()
        self.init_weather_forecast()
        self.init_checks()   


    def _quit(self):
        '''Quits Honu Home'''
        try:
            nw.hangUp()
        except:
            pass
        self.play('./sounds/authno.wav', sfn)
        self.root.quit()
        self.root.destroy()


    def quit_popup(self):
        '''Prompts user to confirm quit'''
        quitq = tkMessageBox.askyesno('Confirm exit', "Are you sure you want to leave Honu Home?")
        if quitq:
            self._quit()        


    def scan_for_location(self):
        '''Gets GPS coordinates of Honu'''
        #self.get_update()
        self.parse_update()
        try: 
            self.latnow.configure(text=self.tupdate['LAT'])#, font=self.fn2, bg='#011239', fg='white')
            self.lonnow.configure(text=self.tupdate['LON'])#, font=self.fn2, bg='#011239', fg='white')
        except:
            self.latnow.configure(text='getting latitude...')#, font=self.fn2, bg='#011239', fg='white')
            self.lonnow.configure(text='getting longitude...')#, font=self.fn2, bg='#011239', fg='white')
        self.root.after(1500, self.scan_for_location)


    def update_display(self):
        '''Updates the dashboard display'''
        #self.get_update()
        try:
            self.parse_update()
            if self.tupdate!='update':
            	self.apply_changes()
        except:
            self.mbox.configure(text='Error updating display')
        #mbox update
        #self.mbox.configure(text=self.inmsg)
        #run
        self.root.after(100, self.update_display)


    def heard(self, phrase):
        '''Reaction to every message that Honu Home receives from Honu'''
        #self.intime = datetime.now()
    	self.incount += 1
        self.datacount += sys.getsizeof(phrase)
        self.inmsg = phrase
        #print self.inmsg
        helper.write_out(phrase, self.remoteaddress, self.incount)


    def call_honu(self):
        '''Connect to Honu using ip address then sends a request for data'''
        nw.call(self.remoteaddress, whenHearCall=self.heard)
        self.get_update()


    def tell_honu(self, outmsg):
        '''Send message to Honu'''
        if nw.isConnected():
            self.outcount += 1
            self.datacount += sys.getsizeof(outmsg)
            nw.say(outmsg)
            #self.outtime = datetime.now()


    def get_update(self):
        '''Ask Honu for data'''
        send = {}
        send['MSG'] = 'DATA'
        self.tell_honu(str(send))


    def parse_update(self):
        '''Parse Honu data'''
    	self.tupdate = 'update'
    	if self.inmsg!='blank':
    		(self.tupdate, self.iupdate) = helper.parse(self.inmsg, self.icon_array)


    def t_parse(self):
        '''Parse Honu data for text updates'''
        self.tupdate = 'update'
        if self.inmsg!='blank':
            self.tupdate = helper.tparse(self.inmsg)


    def init_styles(self):
        '''Initialize Honu Home gui style'''
        #window styles
        self.root.title('Honu Home')
        self.root.configure(bg='#011239')
        self.fn0 = tkFont.Font(family='segoe ui', size=11)
        self.fn1 = tkFont.Font(family='segoe ui', size=8)
        self.fn2 = tkFont.Font(family='segoe ui', size=16)
        self.config_columns()
        self.config_rows()
        self.set_dividers()
        self.icon_array = pd.read_csv('parse_file.csv')


    def init_frames(self):
        '''Initialize Honu Home gui frames'''

        #declare frames
        self.fra = tk.Frame(self.root) #cover screen
        self.fr0 = tk.Frame(self.root) #authentication screen
        self.fr1 = tk.Frame(self.root) #ip selection screen
        self.fr2 = tk.Frame(self.root) #select anchor points
        self.fr3 = tk.Frame(self.root) #pick saved points - no longer necessary, changed to data analytics I
        self.fr4 = tk.Frame(self.root) #confirm anchor points
        self.fr5 = tk.Frame(self.root) #confirm route
        self.fr6 = tk.Frame(self.root) #confirm collection\travel - no longer necessary, changed to weather forecast
        self.fr7 = tk.Frame(self.root) #main monitor
        self.fr8 = tk.Frame(self.root) #confirm stop - no longer necessary, changed to data analytics III
        self.fr9 = tk.Frame(self.root) #confirm home - no longer necessary, changed to data analytics IV
        
        #add to grid
        self.frame_ls = [self.fra, self.fr0, self.fr1, self.fr2, self.fr3, self.fr4, self.fr5, self.fr6, self.fr7, self.fr8, self.fr9]
        for frame in self.frame_ls:
            frame.grid(row=0, column=0, sticky='news')
            frame.configure(bg='#011239')


    def config_columns(self):
        '''Configure columns for Honu Home gui frames'''
        #configure columns
        self.fr7.columnconfigure(4,pad=30, minsize=50)
        self.fr7.columnconfigure(5,pad=90, minsize=75)
        self.fr7.columnconfigure(7,pad=30, minsize=50)
        self.fr7.columnconfigure(8,pad=90, minsize=75)
        self.fr1.columnconfigure(0,pad=100)
        self.fr1.columnconfigure(2,pad=10)
        self.fr1.columnconfigure(3,pad=30)
        self.fr1.columnconfigure(4,pad=10)      
        self.fr2.columnconfigure(0,pad=160)
        self.fr2.columnconfigure(2,pad=160)
        self.fr2.columnconfigure(3,pad=70)
        self.fr2.columnconfigure(4,pad=100)        
        self.fr3.columnconfigure(0, pad=260)      
        self.fr4.columnconfigure(0, pad=260)
        self.fr5.columnconfigure(0, pad=260)       
        self.fr6.columnconfigure(0, pad=140)
        

    def config_rows(self):
        '''Configure rows for Honu Home gui frames'''
        self.fr0.rowconfigure(1,pad=250)
        self.fr1.rowconfigure(1,pad=40)
        self.fr2.rowconfigure(0,pad=50)
        self.fr2.rowconfigure(1,pad=35)
        self.fr2.rowconfigure(2,pad=35)
        self.fr2.rowconfigure(3,pad=40)
        self.fr2.rowconfigure(4,pad=40)
        self.fr2.rowconfigure(5,pad=40)
        self.fr2.rowconfigure(6,pad=20)
        self.fr3.rowconfigure(1,pad=120)
        self.fr5.rowconfigure(1,pad=120)
        self.fr6.rowconfigure(1,pad=120)


    def set_dividers(self):
        '''Make dividers for dashboard'''   
        
        #declare dividers
        self.div1 = tk.Frame(self.fr7, height=5, width=1280, bd=1, bg='#323b51', relief='flat')
        self.div2 = tk.Frame(self.fr7, height=5, width=1280, bd=1, bg='#323b51', relief='flat')
        self.div3 = tk.Frame(self.fr7, height=500, width=5, bd=1, bg='#323b51', relief='flat')
        self.div4 = tk.Frame(self.fr7, height=557, width=5, bd=1, bg='#323b51', relief='flat')
        self.div5 = tk.Frame(self.fr7, height=5, width=1280, bd=1, bg='#323b51', relief='flat')
        
        #add to grid
        self.div1.grid(row=1, columnspan=16, sticky='N')
        self.div2.grid(row=11, columnspan=16, sticky='N')
        self.div3.grid(row=1, column=3, rowspan=10, sticky='N')
        self.div4.grid(row=1, column=9, rowspan=10, sticky='N')
        self.div5.grid(row=13, columnspan=16, sticky='N')


    def init_cover(self):
        '''Initialize cover frame'''
        self.coverbgi = ImageTk.PhotoImage(Image.open('./images/bga.png'))
        self.coverbg = tk.Label(self.fra, image = self.coverbgi, borderwidth=0, highlightthickness=0, bg='#011239')
        self.coverbg.place(x=0, y=0)#, relwidth=1, relheight=1)
        self.step = 0
        self.coverbg.bind('<Button-1>', lambda e: self.slideup())


    def slideup(self):
        '''Slide up transition for cover frame'''
        if self.step < 720:
            self.step += 30
            self.fra.grid(row=0, column=0, pady=(0, self.step))
            self.fra.update()
            self.fra.after(2, self.slideup())
        else:
            self.raise_frame(self.fr0)
            self.fra.grid_forget()
            self.fra.grid(row=0, column=0)


    def init_authentication_screen_set_frames(self):
        '''Initializes frames for authentication screen'''

        #background
        self.authbgi = ImageTk.PhotoImage(Image.open('./images/auth.png'))
        self.authbg = tk.Label(self.fr0, image = self.authbgi, borderwidth=0, highlightthickness=0, bg='#011239')
        self.authbg.place(x=0, y=0)#, relwidth=1, relheight=1)
        
        #button bar
        self.fr0bar = tk.Frame(self.fr0, height=60, width=230, bd=1, bg='#011239', relief='flat')
        self.fr0bar.grid(row=0, column=0, sticky='NW')
        
        #onscreen keyboard
        self.onskfrm = tk.Frame(self.fr0, bd=1, width=810, height=200, bg='black', relief='flat')


    def init_authentication_screen_set_labels(self, destination):
        '''Initializes labels for authentication screen'''

        #declare labels and entry
        self.instr0 = tk.Label(self.fr0, text='Please authenticate to continue.', height=10, width=30, font=self.fn2, bg='#323B51', fg='white', anchor='nw', justify='left', wraplength=360)
        self.pwd = tk.Entry(self.fr0, font=self.fn2, bg='white', fg='#011239', relief='flat', justify='center', width=32, show=u'\u2022')
        self.pwdhold = tk.Label(self.fr0, text='Password', font=self.fn0, bg='white', fg='#00a3fe', justify='left')

        #set entry bindings
        self.pwd.bind('<Return>', lambda e: self.auth(destination))
        self.pwd.bind('<FocusIn>', lambda e: self.holdcheck(self.pwd, self.pwdhold))
        self.pwd.bind('<FocusOut>', lambda e: self.holdcheck(self.pwd, self.pwdhold))
        self.pwdhold.bind('<Button-1>', lambda e: self.holdcheck(self.pwd, self.pwdhold))

        #grid labels and entry
        self.instr0.grid_propagate(False)
        self.instr0.grid(row=2,column=0, sticky='NW')        
        self.pwd.grid_propagate(False)       
        self.pwd.grid(row=1,column=0, columnspan=2, padx=(650,0), sticky='SE', ipady=11)        
        self.pwdhold.grid(row=1, column=0, columnspan=2, padx=(650,0), sticky='S', ipady=11)
        

    def init_authentication_screen_set_buttons(self, power, destination):
        '''Initializes buttons for authentication screen'''
        
        #declare buttons
        self.quit_btn1 = tk.Button(self.fr0bar, relief='flat', bg='black',command=lambda:self.quit_popup())
        self.pin_btn = tk.Button(self.fr0bar, relief='flat', bg='black',command=lambda:self.pin_popup())
        self.onsk_btn = tk.Button(self.fr0bar, relief='flat', bg='black',command=lambda:self.pin_popup())
        self.auth_go = tk.Button(self.fr0, relief='flat', text='go', bg='black', command=lambda:self.auth(destination))
        
        #get icons
        self.q_icon1 = ImageTk.PhotoImage(file='./images/EXIT.gif')
        self.pin_i = ImageTk.PhotoImage(file='./images/PIN.gif')
        self.onsk_btn_i = ImageTk.PhotoImage(file='./images/OSK.gif')
        self.r_arrow1 = ImageTk.PhotoImage(file='./images/R-ARROW.gif')
        
        #apply icons
        self.quit_btn1.config(image=self.q_icon1)
        self.pin_btn.config(image=self.pin_i)
        self.onsk_btn.config(image=self.onsk_btn_i, command=lambda:self.onsk_popup(self.onskfrm, self.onsk_btn, self.pwd, [2,0], True))
        self.auth_go.config(image=self.r_arrow1)
        
        #set tool tips
        self.quit_btn1_tip = tip(self.quit_btn1, 'Shutdown Honu Home')
        self.pin_btn_tip = tip(self.pin_btn, 'Pin sign-in')
        self.onsk_btn_tip = tip(self.onsk_btn, 'Virtual keyboard')

        self.init_authentication_screen_grid_buttons(power)
            
        
    def init_authentication_screen_grid_buttons(self, power):
        '''Grids buttons on authentication screen'''
        self.auth_go.grid(row=1,column=2,sticky='SW')
        if power:
            self.quit_btn1.grid(row=0,column=0,sticky='NW')
            self.pin_btn.grid(row=0,column=1, sticky='NW')
            self.onsk_btn.grid(row=0, column=2, sticky='NW')
        else:
            self.pin_btn.grid(row=0, column=0, sticky='NW')
            self.onsk_btn.grid(row=0, column=1, sticky='NW')


    def init_authentication_screen(self, destination, power):
        '''Initializes the authentication screen'''
        self.init_authentication_screen_set_frames()
        self.init_authentication_screen_set_labels(destination)
        self.init_authentication_screen_set_buttons(power, destination)
        self.pin()
        self.authmode = 'password'
        self.alpha = ''
        self.onsk(self.onskfrm, self.pwd, self.alpha, 1)
        self.pwd.focus_set()


    def holdcheck(self, entry, holder):
        '''Checks to see if entry is in focus and removes placeholder'''
        if (self.root.focus_get() == entry):
            holder.grid_forget()
        elif (entry.get() !=''):
            holder.grid_forget()
        else:
            holder.grid(row=1, column=0, columnspan=2, padx=(650,0), sticky='S', ipady=11)

 
    def onsk_popup(self, frame, button, focus, location, pad): 
        '''Onscreen keyboard pop up'''
        self.pinfrm.grid_forget()
        self.authmode = 'password'
        self.pwdhold.config(text='Password')
        if pad:
            frame.grid(row=location[0], column=location[1], columnspan=6, sticky='NW', padx=(475,10))
        else:
            frame.grid(row=location[0], column=location[1], columnspan=6, sticky='NW')
        button.config(command=lambda:self.onsk_popdn(frame, button, focus, location, pad))
        focus.focus_set()


    def onsk_popdn(self, frame, button, focus, location, pad):
        '''Onscreen keyboard pop down'''
        frame.grid_forget()
        button.config(command=lambda:self.onsk_popup(frame, button, focus, location, pad))


    def auth(self, destination):
        '''Authentication function'''
        if self.authmode == 'password':
            key = 'clearblue'
        elif self.authmode == 'pin':
            key = '12350'
        if self.pwd.get() == key:
            self.raise_frame(destination)
            self.play('./sounds/auth.wav', sfn)
        elif self.pwd.get() != '':
            self.instr0.configure(text='Incorrect '+self.authmode+'.\nPlease authenticate to continue.')
            self.play('./sounds/authno.wav', sfn)


    def pin_popup(self):
        '''Pin keypad pop up'''
        self.authmode = 'pin'
        self.pwdhold.config(text='Pin')
        self.onskfrm.grid_forget()
        self.pinfrm.grid(row=2, column=1, rowspan=3, sticky='NE')
        self.pin_btn.config(command=lambda:self.pin_popdn())
        self.pwd.focus_set()


    def pin_popdn(self):
        '''Pin keypad pop down'''
        self.authmode = 'password'
        self.pwdhold.config(text='Password')
        self.pinfrm.grid_forget()
        self.pin_btn.config(command=lambda:self.pin_popup())


    def pin(self):
        '''Initialize pin keypad'''

        #declare frame
        self.pinfrm = tk.Frame(self.fr0, bd=1, width=50, height=50, bg='#011239', relief='flat')

        #declare buttons
        self.pin7 = tk.Button(self.pinfrm, relief='flat', bg='black', fg='white', width=9, font=self.fn2, command=lambda:self.add_text('7'))
        self.pin8 = tk.Button(self.pinfrm, relief='flat', bg='black', fg='white', width=9, font=self.fn2, command=lambda:self.add_text('8'))
        self.pin9 = tk.Button(self.pinfrm, relief='flat', bg='black', fg='white', width=9, font=self.fn2, command=lambda:self.add_text('9'))
        self.pin4 = tk.Button(self.pinfrm, relief='flat', bg='black', fg='white', width=9, font=self.fn2, command=lambda:self.add_text('4'))
        self.pin5 = tk.Button(self.pinfrm, relief='flat', bg='black', fg='white', width=9, font=self.fn2, command=lambda:self.add_text('5'))
        self.pin6 = tk.Button(self.pinfrm, relief='flat', bg='black', fg='white', width=9, font=self.fn2, command=lambda:self.add_text('6'))
        self.pin1 = tk.Button(self.pinfrm, relief='flat', bg='black', fg='white', width=9, font=self.fn2, command=lambda:self.add_text('1'))
        self.pin2 = tk.Button(self.pinfrm, relief='flat', bg='black', fg='white', width=9, font=self.fn2, command=lambda:self.add_text('2'))
        self.pin3 = tk.Button(self.pinfrm, relief='flat', bg='black', fg='white', width=9, font=self.fn2, command=lambda:self.add_text('3'))
        self.pin0 = tk.Button(self.pinfrm, relief='flat', bg='black', fg='white', width=9, font=self.fn2, command=lambda:self.add_text('0'))
        self.pindel = tk.Button(self.pinfrm, relief='flat', bg='black', fg='white', font=self.fn2, command=lambda:self.backspace())
        self.pinpeep = tk.Button(self.pinfrm, relief='flat', bg='black', fg='white', font=self.fn2)#, command=lambda:self.peep())
        
        #populate buttons
        self.pinbtn = np.array([(self.pin1, self.pin2, self.pin3), (self.pin4, self.pin5, self.pin6), (self.pin7, self.pin8, self.pin9), (self.pinpeep, self.pin0, self.pindel)])
        self.pintxt = np.array([('1', '2', '3'), ('4','5','6'), ('7','8','9'), ('','0', u'\u232B')])
        for i in range(0,4):
            for j in range(0,3):
                self.pinbtn[i,j].config(text=self.pintxt[i,j])
                self.pinbtn[i,j].grid(row=i, column=j, ipady=5, sticky='NESW')


    def onsk1_rows(self, location, array, rows):
        '''Initialize rows for onscreen keyboard 1'''
        self.row10 = tk.Frame(location)
        self.row10.grid(row=0, column=0)
        self.row11 = tk.Frame(location)
        self.row11.grid(row=1, column=0)
        self.row12 = tk.Frame(location)
        self.row12.grid(row=2, column=0)
        self.row13 = tk.Frame(location)
        self.row13.grid(row=3, column=0)
        self.row14 = tk.Frame(location)
        self.row14.grid(row=4, column=0) 
        self.grid_keys(location, array, rows) 


    def onsk2_rows(self, location, array, rows):
        '''Initialize rows for onscreen keyboard 2'''
        self.row20 = tk.Frame(location)
        self.row20.grid(row=0, column=0)
        self.row21 = tk.Frame(location)
        self.row21.grid(row=1, column=0)
        self.row22 = tk.Frame(location)
        self.row22.grid(row=2, column=0)
        self.row23 = tk.Frame(location)
        self.row23.grid(row=3, column=0)
        self.row24 = tk.Frame(location)
        self.row24.grid(row=4, column=0) 
        self.grid_keys(location, array, rows)


    def onsk(self, location, destination, array, rows):
        '''Initialize onscreen keyboard'''
        array = {
            'row0' : ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', u'\u232B'],
            'row1' : ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p','/'],
            'row2' : ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l',','],
            'row3' : ['caps','z', 'x', 'c', 'v', 'b', 'n', 'm','.','?'],
            'row4' : ['@','#','%','*','  space  ','+','-','=']
            }
        if rows == 1:
            self.onsk1_rows(location, array, rows)
        elif rows == 2:
            self.onsk2_rows(location, array, rows)    


    def grid_keys(self, destination, array, rows):
        '''Grid keys on onscreen keyboard'''
        if rows == 1:
            row_set = [self.row10, self.row11, self.row12, self.row13, self.row14]
        elif rows == 2:
            row_set = [self.row20, self.row21, self.row22, self.row23, self.row24]
        for row in array.iterkeys(): # iterate over dictionary of rows
            if row == 'row0':             
                i = 1                     
                for k in array[row]:
                    tk.Button(row_set[0], text=k,width=5, relief='flat', bg='black', fg='white', font=self.fn2, command=lambda k=k: self._attach_key_press(k, destination, array, rows)).grid(row=0,column=i)
                    i += 1
            elif row == 'row1':             
                i = 1                     
                for k in array[row]:
                    tk.Button(row_set[0], text=k,width=5, relief='flat', bg='black', fg='white', font=self.fn2, command=lambda k=k: self._attach_key_press(k, destination, array, rows)).grid(row=1,column=i)
                    i += 1
            elif row == 'row2':
                i = 2
                for k in array[row]:
                    tk.Button(row_set[1], text=k,width=5, relief='flat', bg='black', fg='white', font=self.fn2, command=lambda k=k: self._attach_key_press(k, destination, array, rows)).grid(row=2,column=i)
                    i += 1
            elif row == 'row3':
                i = 2
                for k in array[row]:
                    tk.Button(row_set[2], text=k,width=5, relief='flat', bg='black', fg='white', font=self.fn2, command=lambda k=k: self._attach_key_press(k, destination, array, rows)).grid(row=3,column=i)
                    i += 1
            else:
                i = 3
                for k in array[row]:
                    if k == '  space  ':
                        tk.Button(row_set[3], text=k,width=5, relief='flat', bg='black', fg='white', font=self.fn2, command=lambda k=k: self._attach_key_press(k, destination, array, rows)).grid(row=4,column=i)
                    else:
                        tk.Button(row_set[3], text=k,width=5, relief='flat', bg='black', fg='white', font=self.fn2, command=lambda k=k: self._attach_key_press(k, destination, array, rows)).grid(row=4,column=i)
                    i += 1        
 

    def _attach_key_press(self, k, destination, array, rows):
        '''Process keypress on onscreen keyboard'''
        if k == u'\u232B':
            self.backspace()
        elif k == '  space  ':
            self.add_text(' ')
        elif k == 'caps':
            self.shift_switch(destination, array, rows)
        else:
            self.add_text(k)


    def shift_switch(self, destination, array, rows):
        '''Toggles caps lock on onscreen keyboard'''
        if self.shift==False:
            self.shift = True
            array = {
                'row0' : ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
                'row1' : ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P','/'],
                'row2' : ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L',','],
                'row3' : ['caps','Z', 'X', 'C', 'V', 'B', 'N', 'M','.','?'],
                'row4' : ['@','#','%','*','  space  ','+','-','=']
                }
        elif self.shift==True:
            self.shift = False
            array = {
                'row0' : ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
                'row1' : ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p','/'],
                'row2' : ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l',','],
                'row3' : ['caps','z', 'x', 'c', 'v', 'b', 'n', 'm','.','?'],
                'row4' : ['@','#','%','*','  space  ','+','-','=']
                }            
        self.grid_keys(destination, array, rows)


    def lock_screen(self, screen, power):
        '''Initializes lock screen'''
        self.init_authentication_screen(screen, power)
        self.raise_frame(self.fr0)
        self.play('./sounds/lock.wav', sfn)


    def init_analytics_set_frames_block_1(self):
        '''Initializes block 1'''

        #frame
        self.fr3blk = tk.Frame(self.fr3, height=500, width=500, bd=1, bg='#011239', relief='flat')
        self.fr3blk.grid(row=1,column=2,columnspan=6)
        self.fr3blk.grid_propagate(False)
        self.fr3blk.rowconfigure(1,pad=25)
        self.fr3blk.rowconfigure(7,pad=25)

        #dividers
        self.div3_1 = tk.Frame(self.fr3blk, height=5, width=500, bd=1, bg='#00a3fe', relief='flat')
        self.div3_2 = tk.Frame(self.fr3blk, height=5, width=500, bd=1, bg='#00a3fe', relief='flat')
        self.div3_1.grid(row=1, column=0, columnspan=4)
        self.div3_2.grid(row=7, column=0, columnspan=4)


    def init_analytics_set_frames(self):
        '''Initializes frames for analytics screen'''

        #background
        self.dabgi = ImageTk.PhotoImage(Image.open('./images/allbg.png'))
        self.dabg = tk.Label(self.fr3, image = self.dabgi, borderwidth=0, highlightthickness=0, bg='#011239')
        self.dabg.place(x=0, y=0)#, relwidth=1, relheight=1)

        #block 1
        self.init_analytics_set_frames_block_1()

        #block 2
        self.fr3blk2 = tk.Frame(self.fr3, height=500, width=500, bd=1, bg='#011239', relief='flat')
        self.fr3blk2.grid(row=1,column=2,columnspan=6)
        self.fr3blk2.grid_propagate(False)

        #block 3
        self.fr3blk3 = tk.Frame(self.fr3, height=500, width=500, bd=1, bg='#011239', relief='flat')
        self.fr3blk3.grid(row=1,column=2,columnspan=6)
        self.fr3blk3.grid_propagate(False)

        #button bar
        self.fr3bar = tk.Frame(self.fr3, height=60, width=230, bd=1, bg='#011239', relief='flat')
        self.fr3bar.grid(row=0, column=0, sticky='NW')

        #shuffle group
        self.shuffle_group = [self.fr3blk, self.fr3blk2, self.fr3blk3]
        self.current_graph = self.fr3blk        


    def init_analytics_set_labels(self):
        '''Initializes labels for analytics screen'''
        self.instr5 = tk.Label(self.fr3, text='Welcome to Honu Tools and Insights.', font=self.fn2, bg='#323b51', fg='white',justify='left', height=10, width=30, anchor='nw', wraplength=360)       
        self.instr5.grid_propagate(False)
        self.instr5.grid(row=1, column=0, rowspan=2, sticky='SW')


    def init_analytics_set_buttons(self):
        '''Initializes buttons for analytics screen'''

        #declare buttons
        self.dabk = tk.Button(self.fr3bar, relief='flat', bg='black', command=lambda:self.raise_frame(self.fr1))
        self.lock6 = tk.Button(self.fr3bar, relief='flat', bg='black', command=lambda:self.lock_screen(self.fr3, True))
        self.shuffle = tk.Button(self.fr3bar, relief='flat', bg='black', command=lambda:self.next_up())

        #declare icons
        self.nexti = ImageTk.PhotoImage(Image.open('./images/SCAN.gif'))

        #apply icons
        self.dabk.config(image=self.l_arrow)
        self.lock6.config(image=self.lock_i)
        self.shuffle.config(image=self.nexti)

        #apply tool tips
        self.dabk_tip = tip(self.dabk, 'Return to Honu Selection')
        self.lock6_tip = tip(self.lock6, 'Lock Honu Home')
        self.shuffle_tip = tip(self.shuffle, 'Next tool')

        #grid buttons
        self.dabk.grid(row=0, column=0, sticky='NW')
        self.lock6.grid(row=0,column=2,sticky='NW')
        self.shuffle.grid(row=0, column=1)


    def init_analytics(self):
        '''Initializes the data analytics screen'''
        self.init_analytics_set_frames()
        self.init_analytics_set_labels()
        self.init_analytics_set_buttons()
        self.init_cost_calc()
        self.init_data_graph()
        self.raise_frame(self.current_graph)


    def next_up(self):
        '''Raises the next frame in the shuffle group'''
        current = self.shuffle_group.index(self.current_graph)
        advance = current + 1
        try:
            self.raise_frame(self.shuffle_group[advance])
            self.current_graph = self.shuffle_group[advance]
        except:
            self.raise_frame(self.shuffle_group[0])
            self.current_graph = self.shuffle_group[0]


    def init_data_graph(self):
        '''Plots graph on fr3blk2'''
        #self.cool_plot(self.fr3blk2)


    def init_cost_calc_set_labels(self):
        '''Initializes the cost calculator labels'''

        #header
        self.cost_title = tk.Label(self.fr3blk, text='Honu Fleet Cost Calculator', font=self.fn2, bg='#011239', fg='white')
        self.cost_title.grid(row=0, column=0, columnspan=8)

        #declare labels
        self.fleet_label = tk.Label(self.fr3blk, text='Fleet Size', font=self.fn0, bg='#011239', fg='white', justify='left')
        self.hours_label = tk.Label(self.fr3blk, text='Daily Work Hours', font=self.fn0, bg='#011239', fg='white', justify='left')
        self.GBcost_label = tk.Label(self.fr3blk, text='Data Cost: $/GB', font=self.fn0, bg='#011239', fg='white', justify='left')
        self.kWh_label = tk.Label(self.fr3blk, text='Energy cost: '+u"\u00A2"+'/kWh', font=self.fn0, bg='#011239', fg='white', justify='left')
        self.solar_label = tk.Label(self.fr3blk, text='Daily solar charging hours', font=self.fn0, bg='#011239', fg='white', justify='left')
        self.table_d = tk.Label(self.fr3blk, text='DATA', font=self.fn0, bg='#011239', fg='white')

        #grid labels
        self.fleet_label.grid(row=2,column=0)
        self.hours_label.grid(row=3, column=0)
        self.GBcost_label.grid(row=4, column=0)
        self.kWh_label.grid(row=5, column=0)
        self.solar_label.grid(row=6, column=0)        
        self.table_d.grid(row=8, column=1, sticky='W')        


    def init_cost_calc_set_scales(self):
        '''Initializes the cost calculator scales'''
        self.fleet = tk.Scale(self.fr3blk, from_=0, to=10, orient=tk.HORIZONTAL, length=250, sliderrelief=tk.FLAT, highlightthickness=5, command=self.update_cost)
        self.fleet.grid(row=2, column=1, columnspan=3)
        self.hours = tk.Scale(self.fr3blk, from_=0, to=12, orient=tk.HORIZONTAL, length=250, sliderrelief=tk.FLAT, highlightthickness=5, command=self.update_cost)
        self.hours.grid(row=3, column=1, columnspan=3)
        self.GBcost = tk.Scale(self.fr3blk, from_=0.00, to=50.00, tickinterval=0.01, orient=tk.HORIZONTAL, length=250, sliderrelief=tk.FLAT, highlightthickness=5, command=self.update_cost)
        self.GBcost.grid(row=4, column=1, columnspan=3)
        self.kWh = tk.Scale(self.fr3blk, from_=0.00, to=50, tickinterval=0.01, orient=tk.HORIZONTAL, length=250, sliderrelief=tk.FLAT, highlightthickness=5, command=self.update_cost)
        self.kWh.grid(row=5, column=1, columnspan=3)
        self.solar = tk.Scale(self.fr3blk, from_=0.00, to=12, tickinterval=0.01, orient=tk.HORIZONTAL, length=250, sliderrelief=tk.FLAT, highlightthickness=5, command=self.update_cost)
        self.solar.grid(row=6, column=1, columnspan=3)    


    def init_cost_calc_set_table_hour(self):
        '''Initializes the hourly column of cost calculator'''

        #declare labels
        self.hourly_fc = tk.Label(self.fr3blk, text='HOURLY', font=self.fn0, bg='#011239', fg='white', justify='left')
        self.hourly_d = tk.Label(self.fr3blk, text='$0.00', font=self.fn0, bg='#011239', fg='white')
        self.hourly_e = tk.Label(self.fr3blk, text='$0.00', font=self.fn0, bg='#011239', fg='white')
        self.hourly_t = tk.Label(self.fr3blk, text='$0.00', font=self.fn0, bg='#011239', fg='white')

        #grid labels
        self.hourly_fc.grid(row=9, column=0)
        self.hourly_d.grid(row=9, column=1, sticky='W')
        self.hourly_e.grid(row=9, column=2, sticky='W')
        self.hourly_t.grid(row=9, column=3, sticky='W')


    def init_cost_calc_set_table_day(self):
        '''Initializes the daily column of cost calculator'''
        
        #declare labels
        self.daily_fc = tk.Label(self.fr3blk, text='DAILY', font=self.fn0, bg='#011239', fg='white', justify='left')
        self.daily_d = tk.Label(self.fr3blk, text='$0.00', font=self.fn0, bg='#011239', fg='white')
        self.daily_e = tk.Label(self.fr3blk, text='$0.00', font=self.fn0, bg='#011239', fg='white')
        self.daily_t = tk.Label(self.fr3blk, text='$0.00', font=self.fn0, bg='#011239', fg='white')

        #grid labels
        self.daily_fc.grid(row=10, column=0)
        self.daily_d.grid(row=10, column=1, sticky='W')
        self.daily_e.grid(row=10, column=2, sticky='W')
        self.daily_t.grid(row=10, column=3, sticky='W')


    def init_cost_calc_set_table_week(self):
        '''Initializes the weekly column of cost calculator'''

        #declare labels
        self.weekly_fc = tk.Label(self.fr3blk, text='WEEKLY', font=self.fn0, bg='#011239', fg='white', justify='left')
        self.weekly_d = tk.Label(self.fr3blk, text='$0.00', font=self.fn0, bg='#011239', fg='white')
        self.weekly_e = tk.Label(self.fr3blk, text='$0.00', font=self.fn0, bg='#011239', fg='white')
        self.weekly_t = tk.Label(self.fr3blk, text='$0.00', font=self.fn0, bg='#011239', fg='white')

        #grid labels
        self.weekly_fc.grid(row=11, column=0)
        self.weekly_d.grid(row=11, column=1, sticky='W')
        self.weekly_e.grid(row=11, column=2, sticky='W')
        self.weekly_t.grid(row=11, column=3, sticky='W')


    def init_cost_calc_set_table_month(self):
        '''Initializes the monthly column of cost calculator'''
        
        #declare labels
        self.monthly_fc = tk.Label(self.fr3blk, text='MONTHLY', font=self.fn0, bg='#011239', fg='white', justify='left')
        self.monthly_d = tk.Label(self.fr3blk, text='$0.00', font=self.fn0, bg='#011239', fg='white')
        self.monthly_e = tk.Label(self.fr3blk, text='$0.00', font=self.fn0, bg='#011239', fg='white')
        self.monthly_t = tk.Label(self.fr3blk, text='$0.00', font=self.fn0, bg='#011239', fg='white')

        #grid labels
        self.monthly_fc.grid(row=12, column=0)
        self.monthly_d.grid(row=12, column=1, sticky='W')
        self.monthly_e.grid(row=12, column=2, sticky='W')
        self.monthly_t.grid(row=12, column=3, sticky='W')


    def init_cost_calc_set_table_year(self):
        '''Initializes the yearly column of cost calculator'''    
        
        #declare labels
        self.yearly_fc = tk.Label(self.fr3blk, text='YEARLY', font=self.fn0, bg='#011239', fg='white', justify='left')
        self.yearly_d = tk.Label(self.fr3blk, text='$0.00', font=self.fn0, bg='#011239', fg='white')
        self.yearly_e = tk.Label(self.fr3blk, text='$0.00', font=self.fn0, bg='#011239', fg='white')
        self.yearly_t = tk.Label(self.fr3blk, text='$0.00', font=self.fn0, bg='#011239', fg='white')

        #grid labels
        self.yearly_fc.grid(row=13, column=0)
        self.yearly_d.grid(row=13, column=1, sticky='W')
        self.yearly_e.grid(row=13, column=2, sticky='W')
        self.yearly_t.grid(row=13, column=3, sticky='W')

                        
    def init_cost_calc_set_table(self):
        '''Initializes the cost calculator table'''
        
        #header
        self.table_e = tk.Label(self.fr3blk, text='ENERGY', font=self.fn0, bg='#011239', fg='white')
        self.table_e.grid(row=8, column=2, sticky='W')
        self.table_t = tk.Label(self.fr3blk, text='TOTAL', font=self.fn0, bg='#011239', fg='white')
        self.table_t.grid(row=8, column=3, sticky='W')
        self.init_cost_calc_set_table_hour()
        self.init_cost_calc_set_table_day()
        self.init_cost_calc_set_table_week()
        self.init_cost_calc_set_table_month()
        self.init_cost_calc_set_table_year()


    def init_cost_calc(self):
        '''Initializes cost calculator'''
        self._job = None
        self.init_cost_calc_set_labels()
        self.init_cost_calc_set_scales()
        self.init_cost_calc_set_table()


    def update_cost(self, event):
        '''Calculate cost from sliders'''
        if self._job:
            self.fr3blk.after_cancel(self._job)
        self._job = self.fr3blk.after(5, self.make_change)


    def make_change(self):
        '''Make changes to the tables'''

        #get values    
        fleet = self.fleet.get()
        time = self.hours.get()
        data = self.GBcost.get()
        power = self.kWh.get()
        charge = (13-self.solar.get())/12.0

        #make calculations
        dhourly = (72/1024.0)*data*fleet #power and data values need fixing
        ddaily = dhourly*time
        dweekly = ddaily*7
        dmonthly = dweekly*4
        dyearly = dweekly*52
        phourly = fleet*power*0.03*(charge)
        pdaily = phourly*time
        pweekly = pdaily*7
        pmonthly = pweekly*4
        pyearly = pweekly*52

        #update labels
        labels = [self.hourly_d, self.hourly_e, self.hourly_t, self.daily_d, self.daily_e, self.daily_t, self.weekly_d, self.weekly_e, self.weekly_t, self.monthly_d, self.monthly_e, self.monthly_t, self.yearly_d, self.yearly_e, self.yearly_t]
        values = [str(round(dhourly,2)), str(round(phourly,2)), str(round(dhourly+phourly,2)), str(round(ddaily,2)), str(round(pdaily,2)), str(round(ddaily+pdaily,2)), str(round(dweekly,2)), str(round(pweekly,2)), str(round(dweekly+pweekly,2)), str(round(dmonthly,2)), str(round(pmonthly,2)), str(round(dmonthly+pmonthly,2)), str(round(dyearly,2)), str(round(pyearly,2)), str(round(dyearly+pyearly,2))]
        for i in range(0, len(labels)):
            labels[i].configure(text='$'+values[i])


    def init_ipscreen_prescan(self):
        '''Pre-scans database for ipscreen'''
        self.inmsg = 'blank' #just sticking this here for now
        try:
            self.alldevices = wv.get_ip()
        except:
            self.alldevices = [['','','please re-scan'],['','','please re-scan'],['','','please re-scan']]
        self.honulist = []
        self.one_honu = True
        (self.alldevices, self.avatars) = helper.sort_devices(self.alldevices)
        self.devices = self.alldevices    


    def init_ipscreen_set_frame(self):
        '''Initializes frames for ip screen'''

        #background
        self.ipbgi = ImageTk.PhotoImage(Image.open('./images/ipbg.png'))
        self.ipbg = tk.Label(self.fr1, image = self.ipbgi, borderwidth=0, highlightthickness=0, bg='#011239')
        self.ipbg.place(x=0, y=0)#, relwidth=1, relheight=1)

        #button bar
        self.fr1bar = tk.Frame(self.fr1, height=60, width=230, bd=1, bg='black', relief='flat')
        self.fr1bar.grid(row=0,column=0,rowspan=4, sticky='NW')


    def init_ipscreen_set_labels(self):
        '''Initializes labelss for ip screen'''

        #declare card labels
        self.alias1 = tk.Label(self.fr1, text=self.devices[0][0], font=self.fn0, bg='#323B51', fg='white')
        self.alias2 = tk.Label(self.fr1, text=self.devices[1][0], font=self.fn0, bg='#323B51', fg='white')
        self.alias3 = tk.Label(self.fr1, text=self.devices[2][0], font=self.fn0, bg='#323B51', fg='white')
        self.ip1 = tk.Label(self.fr1, text=self.devices[0][1], font=self.fn0, bg='#323B51', fg='white')
        self.ip2 = tk.Label(self.fr1, text=self.devices[1][1], font=self.fn0, bg='#323B51', fg='white')
        self.ip3 = tk.Label(self.fr1, text=self.devices[2][1], font=self.fn0, bg='#323B51', fg='white')
        self.status1 = tk.Label(self.fr1, text=self.devices[0][2], font=self.fn0, bg='#323B51', fg='white')
        self.status2 = tk.Label(self.fr1, text=self.devices[1][2], font=self.fn0, bg='#323B51', fg='white')
        self.status3 = tk.Label(self.fr1, text=self.devices[2][2], font=self.fn0, bg='#323B51', fg='white')

        #instruction label
        self.instr1 = tk.Label(self.fr1, text='Please select a Honu beach cleaning robot to begin.', font=self.fn2, bg='#323B51', fg='white', justify='left',  height=10, width=30, anchor='nw', wraplength=360)
        self.instr1.grid_propagate(False)
        self.instr1.grid(row=7,column=0, sticky='NW')


    def init_ipscreen_set_buttons_declare_buttons(self):
        '''Declares buttons for initialize ip screen set buttons function'''

        #card navigation
        self.go_honu1 = tk.Button(self.fr1, text='connect', width=25, font=self.fn0, relief='flat', bg='black', fg='white', command=lambda:self.move_on(self.alias1, self.ip1, self.status1))
        self.go_honu2 = tk.Button(self.fr1, text='connect', width=25, font=self.fn0, relief='flat', bg='black', fg='white', command=lambda:self.move_on(self.alias2, self.ip2, self.status2))
        self.go_honu3 = tk.Button(self.fr1, text='connect', width=25, font=self.fn0, relief='flat', bg='black', fg='white', command=lambda:self.move_on(self.alias3, self.ip3, self.status3))
        self.scrl_up1 = tk.Button(self.fr1, relief='flat', bg='black', command=lambda:self.scroll_up())
        self.scrl_dn1 = tk.Button(self.fr1, relief='flat', bg='black', command=lambda:self.scroll_down())

        #button bar
        self.quit_btn = tk.Button(self.fr1bar, relief='flat', bg='black',command=lambda:self.quit_popup())
        self.scan_btn = tk.Button(self.fr1bar, relief='flat', bg='black',command=lambda:self.scan())
        self.data_btn = tk.Button(self.fr1bar, relief='flat', bg='black',command=lambda:self.data_analytics())
        self.mhonu = tk.Button(self.fr1bar, relief='flat', bg='black',command=lambda:self.multi_honu())
        self.chonu = tk.Button(self.fr1bar, relief='flat', bg='black',command=lambda:self.clear_honu())
        self.vhonu = tk.Button(self.fr1bar, relief='flat', bg='black',command=lambda:self.view_honu())
        self.lock1 = tk.Button(self.fr1bar, relief='flat', bg='black', command=lambda:self.lock_screen(self.fr1, True))
        self.searchbtn = tk.Button(self.fr1, relief='flat', bg='black',command=lambda:self.search_honu())
        self.onsk_btn2 = tk.Button(self.fr1bar, relief='flat', bg='black',command=lambda:self.pin_popup())


    def init_ipscreen_set_buttons_declare_icons(self):
        '''Declares icons for initialize ip screen set buttons function'''

        #card navigation
        self.u_arrow = ImageTk.PhotoImage(file='./images/U-ARROW.gif')
        self.l_arrow = ImageTk.PhotoImage(file='./images/L-ARROW.gif')
        self.d_arrow = ImageTk.PhotoImage(file='./images/D-ARROW.gif')
        self.r_arrow = ImageTk.PhotoImage(file='./images/R-ARROW.gif')

        #button bar
        self.q_icon = ImageTk.PhotoImage(file='./images/EXIT.gif')
        self.scan_icon = ImageTk.PhotoImage(file='./images/SCAN.gif')
        self.data_icon = ImageTk.PhotoImage(file='./images/DATA.gif')
        self.mhonu_i = ImageTk.PhotoImage(file='./images/MHONU.gif')
        self.chonu_i = ImageTk.PhotoImage(file='./images/CLEAR.gif')
        self.vhonu_i = ImageTk.PhotoImage(file='./images/VIEW.gif')
        self.lock_i = ImageTk.PhotoImage(file='./images/LOCK.gif')
        self.search_i = ImageTk.PhotoImage(file='./images/SEARCH.gif')
        self.onsk_btn_i2 = ImageTk.PhotoImage(file='./images/OSK.gif')


    def init_ipscreen_set_buttons_apply_icons(self):
        '''Applies icons for initialize ip screen set buttons function'''

        #card navigation
        self.scrl_up1.config(image=self.l_arrow)
        self.scrl_dn1.config(image=self.r_arrow)

        #button bar
        self.quit_btn.config(image=self.q_icon)
        self.scan_btn.config(image=self.scan_icon)
        self.data_btn.config(image=self.data_icon)
        self.mhonu.config(image=self.mhonu_i)
        self.chonu.config(image=self.chonu_i)
        self.vhonu.config(image=self.vhonu_i)
        self.lock1.config(image=self.lock_i)
        self.searchbtn.config(image=self.search_i)
        self.onsk_btn2.config(image=self.onsk_btn_i2, command=lambda:self.onsk_popup(self.onskfrm2, self.onsk_btn2, self.searchbar, [7,1], False))


    def init_ipscreen_set_buttons_apply_tooltips(self):
        '''Applies tooltips for initialize ip screen set buttons function'''
        self.quit_btn_tip = tip(self.quit_btn, 'Shutdown Honu Home')
        self.scan_btn_tip = tip(self.scan_btn, 'Scan for changes')
        self.data_btn_tip = tip(self.data_btn, 'Tools and insights')
        self.mhonu_tip = tip(self.mhonu, 'Toggle fleet mode')
        self.chonu_tip = tip(self.chonu, 'Clear fleet selections')
        self.vhonu_tip = tip(self.vhonu, 'View fleet selections')
        self.lock1_tip = tip(self.lock1, 'Lock Honu Home')
        self.onsk_btn2_tip = tip(self.onsk_btn2, 'Virtual keyboard')


    def init_ipscreen_set_buttons_add_to_grid(self):
        '''Adds to grid for initialize ip screen set buttons function'''
        self.scrl_up1.grid(row=1, column=1, rowspan=5)
        self.scrl_dn1.grid(row=1, column=5, rowspan=5)
        self.quit_btn.grid(row=0,column=0,sticky='NW')
        self.scan_btn.grid(row=0,column=1,sticky='NW')
        self.data_btn.grid(row=0,column=2,sticky='NW')
        self.mhonu.grid(row=0, column=3, sticky='NW')
        self.lock1.grid(row=0,column=8,sticky='NW')
        self.searchbtn.grid(row=6, column=5, sticky='SW')
        self.onsk_btn2.grid(row=0, column=7, sticky='NW')
    

    def init_ipscreen_set_buttons(self):
        '''Initializes buttons for ip screen'''
        self.init_ipscreen_set_buttons_declare_buttons()
        self.init_ipscreen_set_buttons_declare_icons()
        self.init_ipscreen_set_buttons_apply_icons()
        self.init_ipscreen_set_buttons_apply_tooltips()
        self.init_ipscreen_set_buttons_add_to_grid()


    def init_ipscreen_set_cards(self):
        '''Initializes cards for ip screen'''

        #declare avatars
        self.icard1 = ImageTk.PhotoImage(Image.open(self.avatars[0]))
        self.icard2 = ImageTk.PhotoImage(Image.open(self.avatars[1]))
        self.icard3 = ImageTk.PhotoImage(Image.open(self.avatars[2]))

        #apply avatars
        self.card1 = tk.Label(self.fr1, image=self.icard1, borderwidth=0, highlightthickness=0)
        self.card2 = tk.Label(self.fr1, image=self.icard2, borderwidth=0, highlightthickness=0)
        self.card3 = tk.Label(self.fr1, image=self.icard3, borderwidth=0, highlightthickness=0)

        #grid avatars
        self.card1.grid(row=1,column=2, sticky='S')
        self.card2.grid(row=1,column=3, sticky='S')
        self.card3.grid(row=1,column=4, sticky='S')

        #grid alias
        self.alias1.grid(row=2,column=2)
        self.alias2.grid(row=2,column=3)
        self.alias3.grid(row=2,column=4)

        #grid ip address
        self.ip1.grid(row=3,column=2)
        self.ip2.grid(row=3,column=3)
        self.ip3.grid(row=3,column=4)

        #grid status
        self.status1.grid(row=4, column=2)
        self.status2.grid(row=4, column=3)
        self.status3.grid(row=4, column=4)

        #grid buttons
        self.go_honu1.grid(row=5,column=2)
        self.go_honu2.grid(row=5,column=3)
        self.go_honu3.grid(row=5,column=4)        

        self.honu_btn_ls = [self.go_honu1, self.go_honu2, self.go_honu3]


    def init_ipscreen_set_buffer(self):
        '''Initializes buffer for ipscreen'''
        s = ttk.Style()
        #s.theme_use('clam')
        s.configure('blue.Horizontal.TProgressbar', foreground='#00a0ff', background='#00a0ff')#, trough='white')
        self.buffer = ttk.Progressbar(self.fr1, style='blue.Horizontal.TProgressbar', mode='indeterminate', maximum=10, length=670)
        self.buffer.grid(row=6,column=2,columnspan=3,ipady=20,pady=(25,0))


    def init_ipscreen_set_searchbar(self):
        '''Initializes searchbar for ipscreen'''
        self.searchbar = tk.Entry(self.fr1, font=self.fn2, bg='white', fg='#011239', relief='flat', justify='center', width=61)
        self.searchbar.bind('<Return>', lambda e: self.search_honu())
        self.searchbar.grid(row=6,column=2,columnspan=3,ipady=11,pady=(25,0))
        self.onskfrm2 = tk.Frame(self.fr1, bd=1, width=810, height=200, bg='black', relief='flat')
        self.beta = ''
        self.onsk(self.onskfrm2, self.searchbar, self.beta, 2)
        self.searchhold = tk.Label(self.fr1, text='Honu Search', font=self.fn0, bg='white', fg='#00a3fe', justify='left')
        self.searchhold.grid(row=6,column=2,columnspan=3,ipady=11,pady=(25,0))
        self.searchbar.bind('<FocusIn>', lambda e: self.holdcheck2(self.searchbar, self.searchhold))
        self.searchbar.bind('<FocusOut>', lambda e: self.holdcheck2(self.searchbar, self.searchhold))
        self.searchhold.bind('<Button-1>', lambda e: self.holdcheck2(self.searchbar, self.searchhold))


    def init_ipscreen(self):
        '''Initializes ipscren'''
        self.init_ipscreen_prescan()
        self.init_ipscreen_set_frame()
        self.init_ipscreen_set_labels()
        self.init_ipscreen_set_buttons()
        self.init_ipscreen_set_cards()
        self.init_ipscreen_set_buffer()
        self.init_ipscreen_set_searchbar()


    def holdcheck2(self, entry, holder):
        '''Checks focus for entry widget'''
        if (self.root.focus_get() == entry):
            holder.grid_forget()
        elif (entry.get() !=''):
            holder.grid_forget()
        else:
            holder.grid(row=6,column=2,columnspan=3,ipady=11,pady=(25,0))


    def search_honu(self):
        '''Searches honu list'''
        start = time()
        self.query = self.searchbar.get().lower()
        newlist = []
        closes = []
        for honu in self.alldevices:
            searchstring = (honu[0].lower()+' '+honu[1].lower()+' '+honu[2].lower()).split()
            corr = 0
            for word in searchstring:
                sim = SM(None, self.query, word).ratio()
                if self.query in word:
                    sim = 1.0
                if sim > corr:
                    corr = sim
                    close = word
            if corr >= 0.75:
                newlist.append(honu)
                closes.append(close)
        r_count = len(newlist)        
        if len(newlist)>0:
            if r_count != 1:
                s = 's'
                t = 'these'
                s2 = 'es'
            else:
                s = ''
                t = 'this'
                s2 = ''
            (self.devices, self.avatars) = helper.sort_devices(newlist)
            self.repaint_list()
            stop = time()
            length = round((stop-start),3)
            common = Counter(closes).most_common(1)[0][0]
            if common == self.query:
                actual = True
            else:
                actual = False
            if actual==True:
                self.instr1.configure(text='I found '+str(r_count)+' result'+s+' from your query: "'+self.query+'" ('+str(length)+' seconds).\nPlease select a Honu beach cleaning robot to begin.')
            else:
                self.instr1.configure(text='Did you mean "'+str(common)+'"? I included '+t+' match'+s2+' and found '+str(r_count)+' result'+s+' ('+str(length)+' seconds).\nPlease select a Honu beach cleaning robot to begin.')
            self.play('./sounds/auth.wav', sfn)
        else:
            self.instr1.configure(text='I found no results from your query: "'+self.query+'"\nPlease select a Honu beach cleaning robot to begin.')
            self.play('./sounds/authno.wav', sfn)


    def multi_honu(self):
        '''Starts fleet mode selection'''
        self.one_honu = False
        self.chonu.grid(row=1, column=1, sticky='NW')
        self.vhonu.grid(row=1, column=2, sticky='NW')
        self.mhonu.config(command=lambda:self.single_honu())
        self.go_honu1.config(text='select', command=lambda:self.select_honu(self.alias1, self.ip1, self.status1))
        self.go_honu2.config(text='select', command=lambda:self.select_honu(self.alias2, self.ip2, self.status2))
        self.go_honu3.config(text='select', command=lambda:self.select_honu(self.alias3, self.ip3, self.status3))


    def select_honu(self, name, ip, status):
        '''Adds honu to the list in fleet mode'''
        inlist = False
        for item in self.honulist:
            if (item[0].cget('text') == name.cget('text')) and (item[1].cget('text') == ip.cget('text')) and (item[2].cget('text') == status.cget('text')):
                inlist = True
        if inlist == False:
            self.honulist.append([name, ip, status])
            self.instr1.config(text='I added '+name.cget('text')+' to the list. Please select more beach cleaning robots or click/tap the view icon to see the list.')
        else:
            self.instr1.config(text=name.cget('text')+' is already on the list. Please select more beach cleaning robots or click/tap the view icon to see the list.')


    def clear_honu(self):
        '''Clears honu fleet'''
        self.honulist = []
        self.instr1.config(text='I cleared your selections. Please select Honu beach cleaning robots to continue.')


    def view_honu(self):
        '''Views honu fleet'''
        if len(self.honulist) == 0:
            self.honustring = 'You have not selected any Honu beach cleaning robots.\nPlease select Honu beach cleaning robots to continue.'
            popq9 = tkMessageBox.showinfo('View selected',self.honustring)
            self.play('./sounds/connect.wav', sfn)
        else:
            self.honustring = 'NICKNAME\tADDRESS\t\tSTATUS'
            for i in range(0, len(self.honulist)):
                self.honustring += '\n'+str(self.honulist[i][0].cget('text'))+'\t\t'+str(self.honulist[i][1].cget('text'))+'\t'+str(self.honulist[i][2].cget('text'))
            self.honustring += '\nTotal: '+str(len(self.honulist))
            self.honustring += '\nAre you ready to connect?'
            popq8 = tkMessageBox.askyesno('View selected',self.honustring)
            if popq8:
                self.single_honu()
                self.instr1.config(text='Fleet mode is currently unavailable for this version of Honu Home.\nPlease select a Honu beach cleaning robot to begin.')
                self.play('./sounds/connectno.wav', sfn)


    def single_honu(self):
        '''Exits fleet mode'''
        self.one_honu = True
        self.honulist = []
        self.chonu.grid_forget()
        self.vhonu.grid_forget()
        self.mhonu.config(command=lambda:self.multi_honu())
        self.go_honu1.config(text='connect', command=lambda:self.move_on(self.alias1, self.ip1, self.status1))
        self.go_honu2.config(text='connect', command=lambda:self.move_on(self.alias2, self.ip2, self.status2))
        self.go_honu3.config(text='connect', command=lambda:self.move_on(self.alias3, self.ip3, self.status3))
        self.instr1.config(text='Please select a Honu beach cleaning robot to begin.')


    def data_analytics(self):
        '''Goes to data analytics screen'''
        #self.instr1.configure(text='Data analytics is currently unavailable. \nPlease select a honu beach cleaning robot to begin.')
        self.raise_frame(self.fr3)
        self.play('./sounds/mapstep.wav', sfn)


    def scan(self):
        '''Global scan for new honu'''
        self.devices = [['','','scanning...'],['','','scanning...'],['','','scanning...']]
        self.instr1.configure(text='Honu global scan in progress.\nPlease wait.')
        self.buffer.start(600)
        self.searchbar.grid_forget()
        self.searchhold.grid_forget()
        def scanning():
            self.repaint_list()
            self.checkweave()
            self.repaint_list()
            self.play('./sounds/connect.wav', sfn)
            self.instr1.configure(text='I updated the list.\nPlease select a Honu beach cleaning robot to begin.')
            self.searchbar.grid(row=6,column=2,columnspan=3,ipady=11,pady=(25,0))
            self.searchhold.grid(row=6,column=2,columnspan=3,ipady=11,pady=(25,0))
            self.searchbar.bind('<FocusIn>', lambda e: self.holdcheck2(self.searchbar, self.searchhold))
            self.searchbar.bind('<FocusOut>', lambda e: self.holdcheck2(self.searchbar, self.searchhold))
            self.searchhold.bind('<Button-1>', lambda e: self.holdcheck2(self.searchbar, self.searchhold))
            self.buffer.stop()
        t = threading.Thread(target=scanning)
        t.start()


    def checkweave(self):
        '''Checks weaved database for honu'''
        try:
            self.alldevices = wv.get_ip()
        except:
            self.alldevices = [['','','check connection'],['','','check connection'],['','','check connection']]
        (self.alldevices, self.avatars) = helper.sort_devices(self.alldevices)
        self.devices = self.alldevices


    def scroll_down(self):
        '''Scrolls down honu list'''
        self.devices.append(self.devices.pop(0))
        self.avatars.append(self.avatars.pop(0))
        self.repaint_list()
        self.play('./sounds/drip.wav', sfn)


    def scroll_up(self):
        '''Scrolls up honu list'''
        self.devices.insert(0,self.devices[-1])
        self.devices.pop(-1)
        self.avatars.insert(0,self.avatars[-1])
        self.avatars.pop(-1)
        self.repaint_list()
        self.play('./sounds/drip.wav', sfn)


    def repaint_list(self):
        '''Repaints honu list'''
        self.alias1.configure(text=self.devices[0][0])#, font=self.fn2, bg='#011239', fg='white')
        self.alias2.configure(text=self.devices[1][0])#, font=self.fn2, bg='#011239', fg='white')
        self.alias3.configure(text=self.devices[2][0])#, font=self.fn2, bg='#011239', fg='white')
        self.ip1.configure(text=self.devices[0][1])#, font=self.fn2, bg='#011239', fg='white')
        self.ip2.configure(text=self.devices[1][1])#, font=self.fn2, bg='#011239', fg='white')
        self.ip3.configure(text=self.devices[2][1])#, font=self.fn2, bg='#011239', fg='white')
        self.status1.configure(text=self.devices[0][2])#, font=self.fn2, bg='#011239', fg='white')
        self.status2.configure(text=self.devices[1][2])#, font=self.fn2, bg='#011239', fg='white')
        self.status3.configure(text=self.devices[2][2])#, font=self.fn2, bg='#011239', fg='white')
        self.icard1 = ImageTk.PhotoImage(Image.open(self.avatars[0]))
        self.icard2 = ImageTk.PhotoImage(Image.open(self.avatars[1]))
        self.icard3 = ImageTk.PhotoImage(Image.open(self.avatars[2]))
        self.card1.configure(image=self.icard1)
        self.card2.configure(image=self.icard2)
        self.card3.configure(image=self.icard3)


    def move_on(self, name, address, status):
        '''Moves on after selecting honu to connect'''
        ctrlques = tkMessageBox.askyesno('Skip to dashboard', 'Would you like to skip autonomous route planning?')
        (self.remotename, self.remoteaddress, self.remotestatus) = (name.cget('text'), address.cget('text'), status.cget('text'))
        if (self.remotestatus =='active') or (self.remotestatus == 'testing'):
            try:
                self.call_honu()
                if ctrlques:
                    self.pop3active = True
                    self.raise_frame(self.fr8)
                else:
                    self.raise_frame(self.fr2)
                self.play('./sounds/connect.wav', sfn)
            except:
                self.call_error = 'Something seems to be wrong. I could not contact ' + str(self.remotename) + ' at ' + str(self.remoteaddress) + '\nPlease refresh and try again later or select another Honu beach cleaning robot to begin.'
                self.instr1.configure(text=self.call_error)
                self.play('./sounds/connectno.wav', sfn)
                if self.remotename == 'localhost': #get rid of this later
                    if ctrlques:
                        self.raise_frame(self.fr8)
                    else:
                        self.raise_frame(self.fr2)
        elif self.remotestatus == 'inactive':
            self.sleep_error = 'I cannot do that right now. ' + str(self.remotename) + ' is currently unavailable at ' + str(self.remoteaddress) + '.\nPlease select a Honu beach cleaning robot to begin.'
            self.instr1.configure(text=self.sleep_error)
            self.play('./sounds/connectno.wav', sfn)


    def init_anchor_select_screen_set_frame(self):
        '''Initializes frames for anchor select screen'''
        #background
        self.asbgi = ImageTk.PhotoImage(Image.open('./images/anchorsel.png'))
        self.asbg = tk.Label(self.fr2, image = self.asbgi, borderwidth=0, highlightthickness=0, bg='#999999')
        self.asbg.place(x=0, y=0)#, relwidth=1, relheight=1)

        #button bar
        self.fr2bar = tk.Frame(self.fr2, height=60, width=340, bd=1, bg='#011239', relief='flat') #width = 325 for 4 buttons
        self.fr2bar.grid(row=0,column=0,rowspan=4, sticky='NW')

        #onscreen keyboard
        self.oskfrm = tk.Frame(self.fr2, bd=1, width=50, height=50, bg='#011239', relief='flat')
        self._osk(self.oskfrm)


    def init_anchor_select_screen_set_labels_prescan(self):
        '''Does prescan for initialize anchor select screen set labels function'''

        #headers
        self.lathead = tk.Label(self.fr2, text='LATITUDE', font=self.fn0, bg='#323b51', fg='white')
        self.lonhead = tk.Label(self.fr2, text='LONGITUDE', font=self.fn0, bg='#323b51', fg='white')

        #initial location
        try: #will remove for production
            self.latnow = tk.Label(self.fr2, text=self.tupdate['LAT'], font=self.fn0, bg='#323b51', fg='white')
            self.lonnow = tk.Label(self.fr2, text=self.tupdate['LON'], font=self.fn0, bg='#323b51', fg='white')
        except:
            self.latnow = tk.Label(self.fr2, text='getting latitude...', font=self.fn0, bg='#323b51', fg='white')
            self.lonnow = tk.Label(self.fr2, text='getting longitude...', font=self.fn0, bg='#323b51', fg='white')   

        #add to grid
        self.lathead.grid(row=0, column=2)
        self.lonhead.grid(row=0, column=3)
        self.latnow.grid(row=1, column=2)
        self.lonnow.grid(row=1, column=3) 


    def init_anchor_select_screen_set_labels(self):
        '''Initializes labels for anchor select screen'''
        self.init_anchor_select_screen_set_labels_prescan()

        #instructions
        self.instr2 = tk.Label(self.fr2, text="Please tell Honu the boundaries of the work area. The first coordinate is Honu's current position. At least one additional coordinate to plan a route. If you need to enter more than four points, click or tap the + icon.", font=self.fn2, bg='#323b51', fg='white', justify='left', height=10, width=30, anchor='nw', wraplength=360)               
        self.instr2.grid_propagate(False)
        self.instr2.grid(row=6,column=0, rowspan=5, sticky='W') 

        #declare coordinate entries
        self.lat_p1 = tk.Entry(self.fr2, font=self.fn0, bg='#323b51', fg='white', relief='flat', justify='center')
        self.lon_p1 = tk.Entry(self.fr2, font=self.fn0, bg='#323b51', fg='white', relief='flat', justify='center')
        self.lat_p2 = tk.Entry(self.fr2, font=self.fn0, bg='#323b51', fg='white', relief='flat', justify='center')
        self.lon_p2 = tk.Entry(self.fr2, font=self.fn0, bg='#323b51', fg='white', relief='flat', justify='center')
        self.lat_p3 = tk.Entry(self.fr2, font=self.fn0, bg='#323b51', fg='white', relief='flat', justify='center')
        self.lon_p3 = tk.Entry(self.fr2, font=self.fn0, bg='#323b51', fg='white', relief='flat', justify='center')
        self.lat_p4 = tk.Entry(self.fr2, font=self.fn0, bg='#323b51', fg='white', relief='flat', justify='center')
        self.lon_p4 = tk.Entry(self.fr2, font=self.fn0, bg='#323b51', fg='white', relief='flat', justify='center')

        #add to grid
        self.lat_p1.grid(row=2, column=2)
        self.lon_p1.grid(row=2, column=3) 
        self.lat_p2.grid(row=3, column=2)
        self.lon_p2.grid(row=3, column=3) 
        self.lat_p3.grid(row=4, column=2)
        self.lon_p3.grid(row=4, column=3) 
        self.lat_p4.grid(row=5, column=2)
        self.lon_p4.grid(row=5, column=3)

        #initialize anchor points
        self.anchor_ls = [(self.lat_p1, self.lon_p1), (self.lat_p2, self.lon_p2), (self.lat_p3, self.lon_p3), (self.lat_p4, self.lon_p4)]
        self.anchorslat = []
        self.anchorslon = []


    def init_anchor_select_screen_set_buttons(self):
        '''Initializes buttons for anchor select screen'''

        #declare buttons
        self.asbk = tk.Button(self.fr2, relief='flat', bg='black', command=lambda:self.select_new_honu())
        self.asfd = tk.Button(self.fr2, relief='flat', bg='black', command=lambda:self.get_anchors())
        self.more_btn = tk.Button(self.fr2bar, text='more', relief='flat', bg='black')
        self.load_btn = tk.Button(self.fr2bar, text='load', relief='flat', bg='black')
        self.save_btn = tk.Button(self.fr2bar, text='save', relief='flat', bg='black')
        self.view_btn = tk.Button(self.fr2bar, text='view', relief='flat', bg='black')
        self.weather_btn = tk.Button(self.fr2bar, text='forecast', relief='flat', bg='black')
        self.osk_btn = tk.Button(self.fr2bar, text='osk', relief='flat', bg='black')
        self.lock2 = tk.Button(self.fr2bar, relief='flat', bg='black', command=lambda:self.lock_screen(self.fr2, True))

        #declare icons
        self.plus_icon = ImageTk.PhotoImage(file='./images/PLUS.gif')
        self.load_icon = ImageTk.PhotoImage(file='./images/OPEN.gif')
        self.save_icon = ImageTk.PhotoImage(file='./images/SAVE.gif')
        self.view_icon = ImageTk.PhotoImage(file='./images/VIEW.gif')
        self.weather_icon = ImageTk.PhotoImage(file='./images/WEATHER.gif')
        self.osk_icon = ImageTk.PhotoImage(file='./images/OSK.gif')

        #apply icons
        self.asbk.config(image=self.l_arrow)
        self.asfd.config(image=self.r_arrow)
        self.more_btn.config(image=self.plus_icon, command=lambda:self.more_anchors())
        self.load_btn.config(image=self.load_icon, command=lambda:self.load_anchors())
        self.save_btn.config(image=self.save_icon, command=lambda:self.save_anchors())
        self.view_btn.config(image=self.view_icon, command=lambda:self.view_anchors())
        self.weather_btn.config(image=self.weather_icon, command=lambda:self.weatherman())
        self.osk_btn.config(image=self.osk_icon, command=lambda:self.show_osk())
        self.lock2.config(image=self.lock_i)

        #apply tooltips
        self.more_btn_tip = tip(self.more_btn, 'Add points')
        self.load_btn_tip = tip(self.load_btn, 'Load points from file')
        self.save_btn_tip = tip(self.save_btn, 'Save points to file')
        self.view_btn_tip = tip(self.view_btn, 'View points')
        self.weather_btn_tip = tip(self.weather_btn, 'View forecast')
        self.osk_btn_tip = tip(self.osk_btn, 'Virtual keypad')
        self.lock2_tip = tip(self.lock2, 'Lock Honu Home')

        #add to grid
        self.asbk.grid(row=6, column=2)
        self.asfd.grid(row=6, column=3)
        self.more_btn.grid(row=0, column=0, sticky='NW')
        self.load_btn.grid(row=0, column=1, sticky='NW')
        self.save_btn.grid(row=0, column=2, sticky='NW')
        self.view_btn.grid(row=0, column=3, sticky='NW')
        self.weather_btn.grid(row=0, column=4, sticky='NW')
        self.osk_btn.grid(row=0, column=5, sticky='NW')
        self.lock2.grid(row=0,column=6,sticky='NW')


    def init_anchor_select_screen(self):
        '''Initializes anchor select screen'''
        self.init_anchor_select_screen_set_frame()
        self.init_anchor_select_screen_set_labels()
        self.init_anchor_select_screen_set_buttons()
        self.scan_for_location()
 
    def show_osk(self):
        '''Shows onscreen keyboard'''
        self.oskfrm.grid(row=0,column=5,rowspan=8,columnspan=3, sticky='NE')
        self.osk_btn.config(command=lambda:self.hide_osk())


    def hide_osk(self):
        '''Hides onscreen keyboard'''
        self.oskfrm.grid_forget()
        self.osk_btn.config(command=lambda:self.show_osk())


    def _osk(self, frame):
        '''Prepares onscreen keyboard'''
        self.osk7 = tk.Button(frame, relief='flat', bg='black', fg='white', width=4, font=self.fn2, command=lambda:self.add_text('7'))
        self.osk8 = tk.Button(frame, relief='flat', bg='black', fg='white', width=4, font=self.fn2, command=lambda:self.add_text('8'))
        self.osk9 = tk.Button(frame, relief='flat', bg='black', fg='white', width=4, font=self.fn2, command=lambda:self.add_text('9'))
        self.osk4 = tk.Button(frame, relief='flat', bg='black', fg='white', width=4, font=self.fn2, command=lambda:self.add_text('4'))
        self.osk5 = tk.Button(frame, relief='flat', bg='black', fg='white', width=4, font=self.fn2, command=lambda:self.add_text('5'))
        self.osk6 = tk.Button(frame, relief='flat', bg='black', fg='white', width=4, font=self.fn2, command=lambda:self.add_text('6'))
        self.osk1 = tk.Button(frame, relief='flat', bg='black', fg='white', width=4, font=self.fn2, command=lambda:self.add_text('1'))
        self.osk2 = tk.Button(frame, relief='flat', bg='black', fg='white', width=4, font=self.fn2, command=lambda:self.add_text('2'))
        self.osk3 = tk.Button(frame, relief='flat', bg='black', fg='white', width=4, font=self.fn2, command=lambda:self.add_text('3'))
        self.osk0 = tk.Button(frame, relief='flat', bg='black', fg='white', width=4, font=self.fn2, command=lambda:self.add_text('0'))
        self.oskneg = tk.Button(frame, relief='flat', bg='black', fg='white', font=self.fn2, command=lambda:self.neg_text())
        self.oskdel = tk.Button(frame, relief='flat', bg='black', fg='white', font=self.fn2, command=lambda:self.backspace())
        self.oskl = tk.Button(frame, relief='flat', bg='black', fg='white', font=self.fn2, command=lambda:self.cursor_move('l'))
        self.oskdot = tk.Button(frame, relief='flat', bg='black', fg='white', font=self.fn2, command=lambda:self.add_text('.'))
        self.oskr = tk.Button(frame, relief='flat', bg='black', fg='white', font=self.fn2, command=lambda:self.cursor_move('r'))
        self.oskbtn = np.array([(self.osk7, self.osk8, self.osk9), (self.osk4, self.osk5, self.osk6), (self.osk1, self.osk2, self.osk3), (self.osk0, self.oskneg, self.oskdel), (self.oskl, self.oskdot, self.oskr)])
        self.osktxt = np.array([('7', '8', '9'), ('4','5','6'), ('1','2','3'), ('0','+/-',u'\u232B'), ('<','.','>')])
        for i in range(0,5):
            for j in range(0,3):
                self.oskbtn[i,j].config(text=self.osktxt[i,j])
                self.oskbtn[i,j].grid(row=i, column=j, ipady=13, sticky='NESW')


    def add_text(self, text):
        '''Adds text to entry'''
        try:
            string = self.root.focus_get().get()
            if text == '.' and len(string)==0:
                text = '0.'
            if string == '-':
                text = '0.'
            self.root.focus_get().insert('end',text)
            self.play('./sounds/drip.wav', sfn)
        except:
            pass


    def neg_text(self):
        '''Negates entry'''
        try:
            current = self.root.focus_get()
            if current.get() == '':
                self.add_text('-')
            elif current.get()[0] == '-':
                current.delete(0,1)
            else: 
                current.insert(0,'-')
            self.play('./sounds/drip.wav', sfn)
        except:
            pass


    def backspace(self):
        '''Backspace'''
        try:
            current = self.root.focus_get()
            position = current.index('insert')
            string = current.get()
            if len(string) > 0 and position>0:
                new = string[:position-1] + string[position:]
                current.delete(0,'end')
                current.insert('end', new)
                current.icursor(position-1)
            self.play('./sounds/drip.wav', sfn)
        except:
            pass


    def cursor_move(self, direction):
        '''Shifts cursor left or right'''
        try:
            current = self.root.focus_get()
            position = current.index('insert')
            string = current.get()
            if direction == 'l':
                if position > 0:
                    current.icursor(position-1)
            if direction == 'r':
                if position<len(string):
                    current.icursor(position+1)
        except:
            pass


    def select_new_honu(self):
        '''Disconnects and selects a new honu '''
        try:
            nw.hangUp()
        except:
            print 'could not hang up'
        self.instr1.configure(text='Please select a Honu beach cleaning robot to begin.')
        self.raise_frame(self.fr1)
        self.instr2.configure(text="Please tell Honu the boundaries of the work area. The first coordinate is Honu's current position. At least one pair of coordinates needs to be entered. If you need to enter more than four points, click or tap the + icon")#, font=self.fn2, bg='#999999')#, fg='black', justify='left', wraplength=360)


    def get_anchors(self):
        '''Get anchors entered in entry boxes'''
        self.homelat = self.latnow.cget('text')
        self.homelon = self.lonnow.cget('text')
        for anchor in self.anchor_ls:
            if anchor[0].get() != '' and anchor[1].get() != '':
                self.anchorslat.append(anchor[0].get())
                self.anchorslon.append(anchor[1].get())
        if self.valid_check()==True:
            self.display_area()
        else:
            self.instr2.configure(text='Let us try that again. \nPlease tell Honu the boundaries of the work area by entering points in the spaces provided or click/tap the return arrow to select another Honu beach cleaning robot')#, font=self.fn2, bg='#011239', fg='white', justify='left', wraplength=360)
            self.play('./sounds/connectno.wav', sfn)


    def more_anchors(self):
        '''Extend anchor list'''
        for anchor in self.anchor_ls:
            if anchor[0].get() != '' and anchor[1].get() != '':
                self.anchorslat.append(anchor[0].get())
                self.anchorslon.append(anchor[1].get())
                anchor[0].delete(0,'end')
                anchor[1].delete(0,'end')
        self.anchorcount = str(round(((len(self.anchorslat)+len(self.anchorslon))/2.0),1))
        self.instr2.configure(text='I have recorded ' + self.anchorcount+' points. You may enter more points in the spaces provided or click/tap the next arrow to continue')#, font=self.fn2, bg='#011239', fg='white', justify='left', wraplength=360)
        self.play('./sounds/connect.wav', sfn)


    def valid_check(self):
        '''Checks if anchors are valid numbers'''
        errors = 0
        if len(self.anchorslat)<1 or len(self.anchorslon)<1:
            errors += 1
        for lat in self.anchorslat:
            try:
                float(lat)
            except:
                errors += 1
        for lon in self.anchorslon:
            try:
                float(lon)
            except:
                errors += 1
        if errors > 0:
            return False
        else:
            return True


    def load_anchors(self):
        '''Load anchors from file'''
        FILEOPENOPTIONS = dict(defaultextension='.honu',
                  filetypes=[('All files','*.*'), ('Honu file','*.honu')])
        self.loadfile = tkFileDialog.askopenfilename(**FILEOPENOPTIONS)
        try:
            (self.anchorslat, self.anchorslon) = helper.load_anchors(self.loadfile)
            self.instr2.configure(text='I successfully loaded the contents of '+self.loadfile+'.\nYou can view them by clicking the view icon.')
            self.view_anchors()
        except:
            self.instr2.configure(text='Something seems to be wrong. I could not load points from '+self.loadfile)
        #parse filename and add points to anchorslat and anchorslon


    def save_anchors(self):
        '''Save anchors to file'''
        self.savefile = tkFileDialog.asksaveasfilename()
        try:
            helper.save_anchors(self.anchorslat, self.anchorslon, self.savefile)
            self.instr2.configure(text='I successfully saved '+self.anchorcount+' points to '+self.savefile)
        except:
            self.instr2.configure(text='Something seems to be wrong. I could not save the points to '+self.savefile)
        #create anchor file of points in anchorslat and anchorslon


    def view_anchors(self):
        '''View anchors entered'''
        if (len(self.anchorslat) == 0) and (len(self.anchorslon) == 0):
            self.anchorstring = 'You have not entered any anchor points.\nPlease try entering in the spaces provided or loading a file from the disk.'
            popq4 = tkMessageBox.showinfo('View anchor points',self.anchorstring)
        else:
            self.anchorstring = 'You have entered the following anchor points:\nLATITUDE\t\tLONGITUDE'
            for i in range(0, len(self.anchorslat)):
                self.anchorstring += '\n'+self.anchorslat[i]+'\t\t'+self.anchorslon[i]
            self.anchorstring += '\n\nAre they okay? If not I can clear them and start over.'
            popq4 = tkMessageBox.askyesno('View anchor points',self.anchorstring)
            if not popq4:
                self.clear_anchors()
        #self.play('./sounds/connect.wav', sfn)


    def clear_anchors(self):
        '''Clear anchors entered'''
        if len(self.anchorslat)>0:
            popq5 = tkMessageBox.askyesno('Confirm clear anchor points', "This will remove the points you entered. Are you sure?")
            if popq5:
                self.reset_anchors()
                self.play('./sounds/connectno.wav', sfn)


    def display_area(self):
        '''Display work area'''
        (self.boundary, self.sweeparea) = helper.plot_area(self.anchorslat, self.anchorslon)
        if self.sweeparea <= 3000:
            self.acfd.grid(row=2, column=7, sticky='E')
            string = 'This is the area that Honu will work in ('+str(round(self.sweeparea,0))+'m'+u"\u00B2"+'). Please continue if it looks okay, or return to make changes.'
        else:
            string = 'You have entered an area that is '+str(round(self.sweeparea,0))+'m'+u"\u00B2"+'. The maximum area that Honu can sweep is 3000m'+u"\u00B2"+'. Please try again.'
        self.instr3.config(text=string)
        self.plot_points(self.boundary, self.fr4blk)
        self.raise_frame(self.fr4)
        self.play('./sounds/mapstep.wav', sfn)


    def init_anchor_confirmation_screen_frames(self):
        '''Initializes frames for anchor confirmation screen'''

        #background
        self.acbgi = ImageTk.PhotoImage(Image.open('./images/allbg.png'))
        self.acbg = tk.Label(self.fr4, image = self.acbgi, borderwidth=0, highlightthickness=0, bg='#011239')
        self.acbg.place(x=0, y=0)#, relwidth=1, relheight=1)

        #block
        self.fr4blk = tk.Frame(self.fr4, height=423, width=458, bd=1, bg='white', relief='flat')
        self.fr4blk.grid(row=1,column=2,columnspan=6, sticky='S')


    def init_anchor_confirmation_screen_buttons(self):
        '''Initializes buttons for anchor confirmation screen'''

        #declare buttons
        self.acbk = tk.Button(self.fr4, relief='flat', bg='black', command=lambda:self.reset_anchors())
        self.acfd = tk.Button(self.fr4, relief='flat', bg='black', command=lambda:self.display_route())
        self.lock4 = tk.Button(self.fr4, relief='flat', bg='black', command=lambda:self.lock_screen(self.fr4, True))

        #apply icons
        self.acbk.config(image=self.l_arrow)
        self.acfd.config(image=self.r_arrow)
        self.lock4.config(image=self.lock_i)

        #declare tool tip
        self.lock4_tip = tip(self.lock4, 'Lock Honu Home')

        #grid buttons
        self.acbk.grid(row=2, column=2, sticky='W')
        
        self.lock4.grid(row=0,column=0,sticky='NW')


    def init_anchor_confirmation_screen(self):
        '''Initialize anchor confirmation screen'''
        self.init_anchor_confirmation_screen_frames()
        self.init_anchor_confirmation_screen_buttons()

        #instructions
        self.instr3 = tk.Label(self.fr4, text='This is the area', font=self.fn2, bg='#323b51', fg='white', justify='left', height=5, width=30, anchor='nw', wraplength=360)        
        self.instr3.grid_propagate(False)
        self.instr3.grid(row=1, column=0, rowspan=2, sticky='SW')

        self.scan_for_location()


    def go_to_dash(self):
        '''Go to the main screen'''

        self.pop3active = True
        
        #send coordinates screen
        self.buffer2.start(600)
        self.instr3.configure(text='Sending directions to '+self.remotename+'.\nPlease wait.')

        def send_coordinates():
            send = {}
            send['MSG'] = 'GO'
            send['PATH'] = str(self.path)
            send['HLAT'] = str(self.homelat)
            send['HLON'] = str(self.homelon)
            self.tell_honu(str(send))
            print str(send)
            #sleep(3) #get rid of this in production
            self.play('./sounds/mapstep.wav', sfn)
            self.buffer2.stop()
            self.instr3.configure(text=self.remotename+' is enroute. Click or tap next to continue to the live dashboard.')
            self.acfd.configure(command=lambda:self.open_dash())

        v = threading.Thread(target=send_coordinates)
        v.start()


    def open_dash(self):
        '''Open dash board'''
        self.raise_frame(self.fr7)
        self.instr3.config(text='This is the area that Honu will work in. Please continue if it looks okay, or return to make changes.')
        self.instr3.grid_forget()
        self.instr3.grid(row=1, column=0, rowspan=2, sticky='SW')
        self.acfd.config(command=lambda:self.display_route())


    def reset_anchors(self):
        '''Reset anchors'''
        self.anchorslat = []
        self.anchorslon = []
        for anchor in self.anchor_ls:
            anchor[0].delete(0,'end')
            anchor[1].delete(0,'end')
        self.instr2.configure(text="Please tell honu the boundaries of the work area. The first coordinate is honu's current position. At least one additional coordinate to plan a route. If you need to enter more than four points, click or tap the + icon")#, font=self.fn2, bg='#011239', fg='white', justify='left', wraplength=360)
        self.raise_frame(self.fr2)
        self.acfd.config(command=lambda:self.display_route())
        try:
            self.acfd.grid_forget()
        except:
            pass


    def display_route(self):
        '''Display route'''

        self.instr3.configure(text='Calculating route. Please wait')        
        s = ttk.Style()
        #s.theme_use('clam')
        s.configure('blue.Horizontal.TProgressbar', foreground='#00a0ff', background='#00a0ff')#, trough='white')

        self.buffer2 = ttk.Progressbar(self.fr4, style='blue.Horizontal.TProgressbar', mode='indeterminate', maximum=10, length=415)
        self.buffer2.grid(row=1,column=2,columnspan=6, sticky='S')
        self.buffer2.start(600)

        def plotting():
            (self.path, self.distmatrix, self.sweeplength) = helper.plot_path(self.boundary, 2.1)#0.000007) #change to 0.0000007 later
            time = helper.estimate_time(self.sweeplength, self.path)
            string = 'This is the route that Honu will work along ('+str(round(self.sweeplength,0))+'m). Sweep time is approximately '+time+'. Please continue if it looks okay, or return to make changes.'
            self.plot_points(self.path, self.fr4blk)
            self.instr3.configure(text=string)
            self.acfd.configure(command=lambda:self.go_to_dash())
            self.buffer2.stop()
            self.play('./sounds/mapstep.wav', sfn)

        u = threading.Thread(target=plotting)
        u.start()


    def weatherman(self):
        '''Get weather data'''
        self.raise_frame(self.fr6)
        self.unitsys = 'metric'
        (Hfuture, Mfuture, hours, location) = helper.weather() #will be weather(latitude=self.homelat, longitude=self.homelon)
        for i in range(0,5):
            self.hourcast[i].config(text=hours[i])
            self.tempcast[i].config(text=str(round(Hfuture[i, 1],2))+ u"\u00B0")
            self.windcast[i].config(text=str(round(Hfuture[i, 2],2)) + 'm/s')
            self.chancecast[i].config(text=str(100*round(Hfuture[i, 3],2)) + '%')
            self.raincast[i].config(text=str(round(Hfuture[i, 4],2))+ 'mm')
        times = Mfuture[:,0]
        timestamps = []
        for time in times:
            timestamps.append(time.strftime("%Y-%b-%d %I:%M:%S %p"))
        precip = Mfuture[:,1]*100
        intense = Mfuture[:,2]
        self.plot_weather(precip, intense)
        if 'get' in self.homelat.cget('text'):
            string = 'This is the weather forecast for Honu at 40.807812, -73.962138. (near '+location+')'
        else:
            string = 'This is the weather forecast for Honu at '+self.homelat.cget('text')+', '+self.homelon.cget('text')+'. (near '+location+')'
        self.instr6.config(text=string)
        tk.Label(self.fr6blk, text='Powered by Dark Sky', font=self.fn1, bg='#011239', fg='#00a3fe').grid(row=6, column=0, columnspan=5)
        self.unitsysbtn = tk.Button(self.fr6blk, text='USC system', relief='flat', bg='#011239', fg='#00a3fe', command=lambda:self.unit_sys_swap())
        self.unitsysbtn.grid(row=6, column=5)
        send = {}
        send['MSG'] = 'WEATHER'
        send['PRECIP'] = str(precip)
        send['INTENS'] = str(intense)
        send['TIMES'] = str(timestamps)
        self.tell_honu(str(send))


    def temp_convert(self, temp):
        '''Converts betwee Celsius and Fahrenheit'''
        if self.unitsys == 'metric': #switching from celsius to fahrenheit
            newtemp = 32+float(temp[:-1])*9/5
        elif self.unitsys == 'us':
            newtemp = (float(temp[:-1]) - 32)*5/9
        return str(round(newtemp,2))


    def wind_convert(self, wind):
        '''Converts between m/s and mph'''
        if self.unitsys == 'metric': #switching from m/s to mph
            newwind = float(wind[:-3])*2.23694
        elif self.unitsys == 'us':
            newwind = float(wind[:-3])*0.44704
        return str(round(newwind,2))


    def rain_convert(self, rain):
        '''Converts between mm and inches'''
        if self.unitsys == 'metric': #switching from mm to in
            newrain = float(rain[:-2])/25.4
        elif self.unitsys == 'us':
            newrain = float(rain[:-2])*25.4
        return str(round(newrain,2))


    def unit_sys_swap(self):
        for i in range(0,5):
            self.tempcast[i].config(text=self.temp_convert(self.tempcast[i].cget('text'))+ u"\u00B0")
            if self.unitsys == 'metric': #going to us sys
                self.windcast[i].config(text=self.wind_convert(self.windcast[i].cget('text'))+ 'mph')
                self.raincast[i].config(text=self.rain_convert(self.raincast[i].cget('text'))+ 'in')
            elif self.unitsys == 'us':
                self.windcast[i].config(text=self.wind_convert(self.windcast[i].cget('text'))+ 'm/s')
                self.raincast[i].config(text=self.rain_convert(self.raincast[i].cget('text'))+ 'mm')
        if self.unitsys == 'metric':
            self.unitsys = 'us'
            self.unitsysbtn.config(text='metric system')
        elif self.unitsys == 'us':
            self.unitsys = 'metric'
            self.unitsysbtn.config(text='USC system')




    def plot_weather(self, hours, hours2):
        '''Plot weather data'''
        x = hours
        y = hours2
        f = Figure(figsize=(4.5, 2.25), dpi=100)
        a = f.add_subplot(111)#, axisbg='#FFF5E5')
        a.plot(x, color='green')
        b = f.add_subplot(111, sharex=a, frameon=False)
        b.plot(y, color='blue')
        self.pfont = {'fontname':'segoe ui', 'size':8}
        self.qfont = {'fontname':'segoe ui', 'size':8, 'color':'blue'}
        self.rfont = {'fontname':'segoe ui', 'size':8, 'color':'green'}
        a.set_xlabel('minutes after the hour', **self.pfont)
        a.set_ylabel('chance of rain (%)', **self.qfont)
        b.set_ylabel('expected rainfall (mm)', **self.rfont)
        b.yaxis.set_label_position('right')
        b.yaxis.tick_right()
        a.set_title('Rain Forecast', **self.pfont)
        a.set_ylim([-5, 100])
        if max(y) < 1:
            b.set_ylim([-0.05,1])
        else:
            b.set_ylim([0, max(y)*1.1])
        a.tick_params(axis='both', which='major', labelsize=8)
        a.tick_params(axis='both', which='minor', labelsize=8)
        b.tick_params(axis='both', which='major', labelsize=8)
        b.tick_params(axis='both', which='minor', labelsize=8)
        #a.legend(loc='upper left', prop={'size':8})
        #b.legend(loc='upper right', prop={'size':8})
        f.tight_layout()
        canvas = FigureCanvasTkAgg(f, master=self.fr6blk)
        canvas.get_tk_widget().grid(row=5, column=0, columnspan=6, sticky='NESW')#, sticky='NESW')


    def init_weather_forecast(self):
        '''Initialize weather forecast screen'''
        self.wfbgi = ImageTk.PhotoImage(Image.open('./images/allbg.png'))
        self.wfbg = tk.Label(self.fr6, image = self.wfbgi, borderwidth=0, highlightthickness=0, bg='#011239')
        self.wfbg.place(x=0, y=0)#, relwidth=1, relheight=1)
        self.fr6bar = tk.Frame(self.fr6, height=60, width=230, bd=1, bg='#011239', relief='flat')
        self.fr6bar.grid(row=0, column=0, sticky='NW')
        self.instr6 = tk.Label(self.fr6, text='This is the weather forecast for Honu.', font=self.fn2, bg='#323b51', fg='white', justify='left', height=8, width=30, anchor='nw', wraplength=360)        
        self.instr6.grid_propagate(False)
        self.fr6blk = tk.Frame(self.fr6, height=423, width=610, bd=1, bg='#011239', relief='flat')
        self.fr6blk.grid(row=1,column=2,columnspan=6, sticky='S')
        #self.fr6blk.grid_propagate(False)
        self.wfbk = tk.Button(self.fr6bar, relief='flat', bg='black', command=lambda:self.raise_frame(self.fr2))
        #self.wffd = tk.Button(self.fr6, relief='flat', bg='black')#, command=lambda:self.go_to_dash())
        self.wfbk.config(image=self.l_arrow)
        #self.wffd.config(image=self.r_arrow)
        self.wfbk.grid(row=0, column=0, sticky='NW')
        #self.wffd.grid(row=2, column=7, sticky='E')
        self.instr6.grid(row=1, column=0, padx=(30,0), sticky='SW')
        self.lock7 = tk.Button(self.fr6bar, relief='flat', bg='black', command=lambda:self.lock_screen(self.fr6, True))
        self.lock7_tip = tip(self.lock7, 'Lock Honu Home')
        self.lock7.config(image=self.lock_i)
        self.lock7.grid(row=0,column=1, sticky='NW')
        (self.H1, self.H2, self.H3, self.H4, self.H5) = (None, None, None, None, None) 
        (self.T1, self.T2, self.T3, self.T4, self.T5) = (None, None, None, None, None) 
        (self.S1, self.S2, self.S3, self.S4, self.S5) = (None, None, None, None, None) 
        (self.P1, self.P2, self.P3, self.P4, self.P5) = (None, None, None, None, None) 
        (self.N1, self.N2, self.N3, self.N4, self.N5) = (None, None, None, None, None)
        self.hourcast = [self.H1, self.H2, self.H3, self.H4, self.H5]
        self.tempcast = [self.T1, self.T2, self.T3, self.T4, self.T5]
        self.windcast = [self.S1, self.S2, self.S3, self.S4, self.S5]
        self.chancecast = [self.P1, self.P2, self.P3, self.P4, self.P5]
        self.raincast = [self.N1, self.N2, self.N3, self.N4, self.N5]
        tk.Label(self.fr6blk, text='Temperature', font=self.fn1, bg='#011239', fg='white').grid(row=1, column=0)
        tk.Label(self.fr6blk, text='Wind speed', font=self.fn1, bg='#011239', fg='white').grid(row=2, column=0)
        tk.Label(self.fr6blk, text='Chance of rain', font=self.fn1, bg='#011239', fg='white').grid(row=3, column=0)
        tk.Label(self.fr6blk, text='Precipitation', font=self.fn1, bg='#011239', fg='white').grid(row=4, column=0)
        for j in range(0,5):
            self.fr6blk.rowconfigure(j,pad=20)
            self.fr6blk.columnconfigure(j+1, pad=60)
            self.hourcast[j] = tk.Label(self.fr6blk, text='H', font=self.fn0, bg='#011239', fg='white')
            self.tempcast[j] = tk.Label(self.fr6blk, text='T', font=self.fn0, bg='#011239', fg='white')
            self.windcast[j] = tk.Label(self.fr6blk, text='W', font=self.fn0, bg='#011239', fg='white')
            self.chancecast[j] = tk.Label(self.fr6blk, text='P', font=self.fn0, bg='#011239', fg='white')
            self.raincast[j] = tk.Label(self.fr6blk, text='N', font=self.fn0, bg='#011239', fg='white')
            self.hourcast[j].grid(row=0, column=j+1)
            self.tempcast[j].grid(row=1, column=j+1)
            self.windcast[j].grid(row=2, column=j+1)
            self.chancecast[j].grid(row=3, column=j+1)
            self.raincast[j].grid(row=4, column=j+1)


    def init_main_screen(self):
        self.init_header()
        self.init_dashboard()
        self.init_sensor_data()
        self.init_obstacle_data()
        self.init_spatial_data()
        self.init_map()
        self.init_footer()
        #self.call_honu()
        self.update_display()


    def init_header(self):
        #logo
        self.logoi = ImageTk.PhotoImage(Image.open('./images/logo.gif'))
        self.logo = tk.Label(self.fr7, image=self.logoi, borderwidth=0, highlightthickness=0, bg='#011239')
        self.logo.grid(row=0, column=0, columnspan=3, sticky='W')
        #datetime - define labels
        self.date = tk.Label(self.fr7, text='Date: ', font=self.fn0, bg='#011239', fg='white') #from PC or GPS
        self.time = tk.Label(self.fr7, text='Time: ', font=self.fn0, bg='#011239', fg='white') #from PC or GPS
        #datetime - add to grid
        self.date.grid(row=0,column=12, columnspan=2)
        self.time.grid(row=0,column=14, columnspan=2)
        #buttons
        self.msbk = tk.Button(self.fr7, relief='flat', bg='black', command=lambda:self.popup1())
        self.msbk.config(image=self.l_arrow)
        self.msbk.grid(row=0, column=3,columnspan=2)
        self.home_icon = ImageTk.PhotoImage(file='./images/HOME.gif')
        self.home = tk.Button(self.fr7, relief='flat', bg='black', command=lambda:self.popup2())
        self.home_tip = tip(self.home, 'Call Honu to home base')
        self.home.config(image=self.home_icon)
        self.home.grid(row=0,column=5,columnspan=2)
        self.lock7 = tk.Button(self.fr7, relief='flat', bg='black', command=lambda:self.lock_screen(self.fr7, False))
        self.lock7_tip = tip(self.lock7, 'Lock Honu Home')
        self.lock7.config(image=self.lock_i)
        self.lock7.grid(row=0,column=7,columnspan=2)
        self.scan_for_location()
        #control indicator
        self.CTRLi = ImageTk.PhotoImage(Image.open('./images/AUTO.gif'))
        self.ctrl0 = './images/AUTO.gif'
        self.pop3active = False
        self.CTRL=tk.Label(self.fr7, image=self.CTRLi, borderwidth=0, highlightthickness=0)
        self.CTRL.grid(row=0, column=9, columnspan=3, sticky='W')


    def popup1(self):
        popq1 = tkMessageBox.askyesno('Confirm re-route', "This will stop Honu's current operation and return to route planning. Are you sure?")
        if popq1:
            send = {}
            send['MSG'] = 'STOP'
            self.tell_honu(str(send))
            self.reset_anchors()
            self.play('./sounds/connectno.wav', sfn)


    def popup2(self):
        popq1 = tkMessageBox.askyesno('Confirm return home', "This will stop the current operation and cause Honu to return home. Are you sure?")
        if popq1:
            send = {}
            send['MSG'] = 'STOP'
            self.tell_honu(str(send))
            self.play('./sounds/connectno.wav', sfn)
            popq6 = tkMessageBox.askyesno('Confirm home position', 'Honu will return to '+self.homelat.cget('text')+', '+self.homelon.cget('text')+'. Is that okay?')
            if popq6:
                #do some stuff with the anchors
                self.raise_frame(self.fr4)
                self.play('./sounds/connectno.wav', sfn)
            else:
                self.popup7()
                '''
                popq7 = tkSimpleDialog.askstring('Set home coordinates', 'Please enter home coordinates in the format "latitude, longitude": ')
                if popq7:
                    #do some stuff with anchors
                    self.raise_frame(self.fr5)
                    self.play('./sounds/connectno.wav', sfn)
                '''

    def set_home(self):
        self.popq7.destroy()
        self.raise_frame(self.fr4)
        self.play('./sounds/connectno.wav', sfn)


    def popup7(self):
        self.popq7 = tk.Tk()
        self.popq7.iconbitmap('./images/favicon.ico')
        self.popq7.title('Set home position')
        self.popq7.configure(bg='#011239')
        self.homeinstr = tk.Label(self.popq7, text='Please enter the GPS coordinates of the homing position.', font=self.fn1, bg='#011239', fg='white')#, justify='left',  height=10, width=30)
        self.hlatlabel = tk.Label(self.popq7, text='LATITUDE', font=self.fn0, bg='#011239', fg='white')#,  height=10, width=30)
        self.hlonlabel =tk.Label(self.popq7, text='LONGITUDE', font=self.fn0, bg='#011239', fg='white')#,  height=10, width=30)
        self.homelatl = tk.Entry(self.popq7, font=self.fn0, bg='white', fg='black')#, justify='left',  height=10, width=30)
        self.homelonl = tk.Entry(self.popq7, font=self.fn0, bg='white', fg='black')#, justify='left',  height=10, width=30)
        self.homefd = tk.Button(self.popq7, text='OK', font=self.fn0, relief='flat', bg='black', fg='white', command=lambda:self.set_home())
        self.homeinstr.grid(row=0, column=0, columnspan=3)
        self.hlatlabel.grid(row=1, column=0)
        self.hlonlabel.grid(row=3, column=0)
        self.homelat.grid(row=2, column=0)
        self.homelon.grid(row=4, column=0)
        self.homefd.grid(row=6, column=1)
        self.oskfrm2 = tk.Frame(self.popq7, bd=1, width=50, height=50, bg='#011239', relief='flat')
        self._osk(self.oskfrm2)
        self.oskfrm2.grid(row=1, column=2, rowspan=7)
        self.popq7.update()


    def popup3(self):
        popq3 = tkMessageBox.askyesno('Confirm re-route', "Honu has just re-entered autonomous control. Would you like to return to route planning?")
        if popq3:
            self.pop3active = False
            self.reset_anchors()
            self.play('./sounds/connectno.wav', sfn)


    def init_dashboard(self):
        self.init_dash_IR()
        self.init_dash_MO()
        self.init_dash_INDI()
        self.init_dash_MBOX()


    def init_dash_IR(self):
        #IR obstacle sensors - load state 0 images
        self.LIRi = ImageTk.PhotoImage(Image.open('./images/LIR-0.gif'))
        self.FIRi = ImageTk.PhotoImage(Image.open('./images/FIR-0.gif'))
        self.RIRi = ImageTk.PhotoImage(Image.open('./images/RIR-0.gif'))
        self.BIRi = ImageTk.PhotoImage(Image.open('./images/BIR-0.gif'))
        #IR sensors define labels
        self.RIR=tk.Label(self.fr7, image=self.RIRi, borderwidth=0, highlightthickness=0)
        self.LIR=tk.Label(self.fr7, image=self.LIRi, borderwidth=0, highlightthickness=0)
        self.FIR=tk.Label(self.fr7, image=self.FIRi, borderwidth=0, highlightthickness=0)
        self.BIR=tk.Label(self.fr7, image=self.BIRi, borderwidth=0, highlightthickness=0)
        #IR sensors - add to grid
        self.RIR.grid(row=2, column=2, rowspan=2)
        self.LIR.grid(row=2, column=0, rowspan=2)
        self.FIR.grid(row=2, column=1)
        self.BIR.grid(row=6, column=1)


    def init_dash_MO(self):
        #motors - load state 0 images
        self.LMOi = ImageTk.PhotoImage(Image.open('./images/LMO-0.gif'))
        self.RMOi = ImageTk.PhotoImage(Image.open('./images/RMO-0.gif'))
        self.CMOi = ImageTk.PhotoImage(Image.open('./images/CMO-0.gif'))
        #motors - define labels
        self.LMO=tk.Label(self.fr7, image=self.LMOi, borderwidth=0, highlightthickness=0)
        self.RMO=tk.Label(self.fr7, image=self.RMOi, borderwidth=0, highlightthickness=0)
        self.CMO=tk.Label(self.fr7, image=self.CMOi, borderwidth=0, highlightthickness=0)
        #motors - add to grid
        self.LMO.grid(row=4, column=0, rowspan=3)
        self.RMO.grid(row=4, column=2, rowspan=3)
        self.CMO.grid(row=3, column=1)


    def init_dash_INDI(self):
        #indicators - load state 0  images
        self.INDi = ImageTk.PhotoImage(Image.open('./images/IND-0.gif'))
        self.DOORi = ImageTk.PhotoImage(Image.open('./images/DOOR-0.gif'))
        #indicators - define labels
        self.IND=tk.Label(self.fr7, image=self.INDi, borderwidth=0, highlightthickness=0)
        self.DOOR=tk.Label(self.fr7, image=self.DOORi, borderwidth=0, highlightthickness=0)
        #indicators - add to grid
        self.IND.grid(row=4, column=1)
        self.DOOR.grid(row=5, column=1)


    def init_dash_MBOX(self):
        #message box
        self.mboxfrm = tk.Frame(self.fr7, height=120, width=810, bd=1, bg='#323b51', relief='flat')
        self.mboxlabel = tk.Label(self.mboxfrm, text='Messages', font=self.fn1, bg='#323b51', fg='white')
        self.mbox = tk.Label(self.mboxfrm,text='Busy bantering with bored beachgoers', font=self.fn0, bg='#323b51', fg='white', wraplength=420)
        self.mboxfrm.grid_propagate(False)
        self.mboxfrm.grid(row=7,column=0,columnspan=9,rowspan=3, sticky='E')
        self.mboxlabel.grid(row=0, column=0, columnspan=9, sticky='W')
        self.mbox.grid(row=1, column=0, rowspan=2, columnspan=10, sticky='NW')


    def init_sensor_data(self):
        self.init_sensor_data_ID()
        self.init_sensor_data_vars()

    
    def init_sensor_data_ID(self):
        #data is (words to be changed into images) - define labels
        self.speed_i = ImageTk.PhotoImage(Image.open('./images/SPD-X.gif'))
        self.battery_i = ImageTk.PhotoImage(Image.open('./images/BAT-F.gif'))
        self.comb_i = ImageTk.PhotoImage(Image.open('./images/CMB-0.gif'))
        self.temp_i = ImageTk.PhotoImage(Image.open('./images/TMP-X.gif'))
        self.humid_i = ImageTk.PhotoImage(Image.open('./images/HMD-X.gif'))
        self.vol_i = ImageTk.PhotoImage(Image.open('./images/VOL-X.gif'))
        self.speedi = tk.Label(self.fr7, image=self.speed_i, bg='#011239', borderwidth=0, highlightthickness=0) #from GPS
        self.batteryi = tk.Label(self.fr7, image=self.battery_i, bg='#011239', borderwidth=0, highlightthickness=0) #from volie
        self.combi = tk.Label(self.fr7, image=self.comb_i, bg='#011239', borderwidth=0, highlightthickness=0) #from current
        self.tempi = tk.Label(self.fr7, image=self.temp_i, bg='#011239', borderwidth=0, highlightthickness=0) #from humidity sensor
        self.humidi = tk.Label(self.fr7, image=self.humid_i, bg='#011239', borderwidth=0, highlightthickness=0) #from humidity sensor
        self.voli = tk.Label(self.fr7, image=self.vol_i, bg='#011239', borderwidth=0, highlightthickness=0) #from internal IR
        #data is - add to grid
        self.speedi.grid(row=2,column=4)
        self.batteryi.grid(row=3,column=4)
        self.combi.grid(row=4,column=4)
        self.tempi.grid(row=5,column=4)
        self.humidi.grid(row=6,column=4)
        self.voli.grid(row=2,column=7)


    def init_sensor_data_vars(self):
        #data (values to be updated) - define labels
        self.speed = tk.Label(self.fr7, text='SPD ', font=self.fn0, bg='#011239', fg='white') #from GPS
        self.battery = tk.Label(self.fr7, text='BAT ', font=self.fn0, bg='#011239', fg='white') #from volie
        self.comb = tk.Label(self.fr7, text='CMB ', font=self.fn0, bg='#011239', fg='white') #from current
        self.temp = tk.Label(self.fr7, text='TMP ', font=self.fn0, bg='#011239', fg='white') #from humidity sensor
        self.humid = tk.Label(self.fr7, text='HUM ', font=self.fn0, bg='#011239', fg='white') #from humidity sensor
        self.vol = tk.Label(self.fr7, text='VOL ', font=self.fn0, bg='#011239', fg='white') #from internal IR
        #data - add to grid
        self.speed.grid(row=2,column=5)
        self.battery.grid(row=3,column=5)
        self.comb.grid(row=4,column=5)
        self.temp.grid(row=5,column=5)
        self.humid.grid(row=6,column=5)
        self.vol.grid(row=2,column=8)


    def init_obstacle_data(self):
        #obstacle is (words to be changed into images) - define labels
        self.front_i = ImageTk.PhotoImage(Image.open('./images/FIR-X.gif'))
        self.left_i = ImageTk.PhotoImage(Image.open('./images/LIR-X.gif'))
        self.right_i = ImageTk.PhotoImage(Image.open('./images/RIR-X.gif'))
        self.rear_i = ImageTk.PhotoImage(Image.open('./images/BIR-X.gif'))
        self.fronti = tk.Label(self.fr7, image=self.front_i, bg='#011239', borderwidth=0, highlightthickness=0) #from front IR
        self.lefti = tk.Label(self.fr7, image=self.left_i, bg='#011239', borderwidth=0, highlightthickness=0) #from left IR
        self.righti = tk.Label(self.fr7, image=self.right_i, bg='#011239', borderwidth=0, highlightthickness=0) #from right IR
        self.reari = tk.Label(self.fr7, image=self.rear_i, bg='#011239', borderwidth=0, highlightthickness=0) #from rear IR
        #obstacle is - add to grid
        self.fronti.grid(row=3,column=7)
        self.lefti.grid(row=4,column=7)
        self.righti.grid(row=5,column=7)
        self.reari.grid(row=6,column=7)
        #obstacles (values to be updated) - define labels
        self.front = tk.Label(self.fr7, text='F ', font=self.fn0, bg='#011239', fg='white') #from front IR
        self.left = tk.Label(self.fr7, text='L ', font=self.fn0, bg='#011239', fg='white') #from left IR
        self.right = tk.Label(self.fr7, text='R ', font=self.fn0, bg='#011239', fg='white') #from right IR
        self.rear = tk.Label(self.fr7, text='B ', font=self.fn0, bg='#011239', fg='white') #from rear IR
        #obstacles - add to grid
        self.front.grid(row=3,column=8)
        self.left.grid(row=4,column=8)
        self.right.grid(row=5,column=8)
        self.rear.grid(row=6,column=8)


    def init_spatial_data(self):
        #spatial is
        self.lati = tk.Label(self.fr7, text='LAT: ', font=self.fn0, bg='#011239', fg='white') #from GPS
        self.loni = tk.Label(self.fr7, text='LON: ', font=self.fn0, bg='#011239', fg='white') #from GPS
        self.alti = tk.Label(self.fr7, text='ALT: ', font=self.fn0, bg='#011239', fg='white') #from GPS)
        self.vnoi = tk.Label(self.fr7, text='VISITED: ', font=self.fn0, bg='#011239', fg='white') #from algo
        self.rnoi = tk.Label(self.fr7, text='REMAINING: ', font=self.fn0, bg='#011239', fg='white') #from algo
        self.cpsi = tk.Label(self.fr7, text='BEARING: ', font=self.fn0, bg='#011239', fg='white') #from GPS
        #spatial is - add to grid
        self.lati.grid(row=7,column=11, sticky='W')
        self.loni.grid(row=8,column=11, sticky='W')
        self.alti.grid(row=9,column=11, sticky='W')
        self.vnoi.grid(row=7,column=14, sticky='W')
        self.rnoi.grid(row=8,column=14, sticky='W')
        self.cpsi.grid(row=9,column=14, sticky='W')
        #spatial (values to be updated) - define labels
        self.lat = tk.Label(self.fr7, text='LAT ', font=self.fn0, bg='#011239', fg='white') #from GPS
        self.lon = tk.Label(self.fr7, text='LON ', font=self.fn0, bg='#011239', fg='white') #from GPS
        self.alt = tk.Label(self.fr7, text='ALT ', font=self.fn0, bg='#011239', fg='white') #from GPS
        self.vn = tk.Label(self.fr7, text='VIS ', font=self.fn0, bg='#011239', fg='white') #from algo
        self.rn = tk.Label(self.fr7, text='REM ', font=self.fn0, bg='#011239', fg='white') #from algo
        self.cps_i = ImageTk.PhotoImage(Image.open('./images/CPS-X.gif').convert('RGBA').rotate(90))
        self.cps = tk.Label(self.fr7, image=self.cps_i, bg='#011239', borderwidth=0, highlightthickness=0) #from GPS
        #obstacles - add to grid
        self.lat.grid(row=7,column=12)
        self.lon.grid(row=8,column=12)
        self.alt.grid(row=9,column=12)
        self.vn.grid(row=7,column=15)
        self.rn.grid(row=8,column=15)
        self.cps.grid(row=9,column=15)


    def init_map(self):
        #map
        self.mapi = ImageTk.PhotoImage(Image.open('./images/MAP.gif'))
        self.map = tk.Label(self.fr7, image=self.mapi, borderwidth=4, highlightthickness=4, bg='#011239')
        self.map.grid(row=2, column=10, columnspan=6, rowspan=5, sticky='N')


    def init_footer(self):
        #session
        self.sessioni = tk.Label(self.fr7, text='Session Info: ', font=self.fn0, bg='#011239', fg='white')
        self.sessioni.grid(row=12,column=0)
        #get info
        self.hostname = socket.gethostname()
        self.hostaddress = socket.gethostbyname(self.hostname)
        self.remotename, self.remoteaddress = ('Device Alias', 'Device Address')
        self.incount = 0
        self.outcount = 0
        self.datacount = 0
        self.sessionstr = '  Hostname: ' + self.hostname + '  | Host Address: ' + self.hostaddress + '  | Remote: ' + self.remotename + '  | Remote Address: ' + self.remoteaddress + '  | Sent: ' + str(self.outcount) + '  | Received: ' + str(self.incount) + '  |Data Exchanged: ' + str(self.datacount)
        self.session = tk.Label(self.fr7, text=self.sessionstr, font=self.fn0, bg='#011239', fg='white')
        self.session.grid(row=12,column=1, columnspan=15, sticky='W')
        #copyright info
        self.foot = tk.Label(self.fr7, text='Copyright '+ u'\xa9' + ' 2017', font=self.fn1, bg='#011239', fg='white')
        self.foot.grid(row=14,columnspan=16)


    def init_checks(self):
        title = 'Honu Home 3.9'
        message = 'System Checks\nNetwork: OK\nModules: OK\nDatabase: OK'
        def win_popup():
            pop = WindowsBalloonTip(title, message)
        w = threading.Thread(target=win_popup)
        w.start()
        

    def apply_changes(self):
    	self.header_changes()
    	self.dashboard_changes()
    	self.update_sensor_icons()
    	self.update_sensor_values()
    	self.update_clearance_values()
    	self.update_spatial_data()
    	self.update_footer()


    def header_changes(self):
    	datestr = self.tupdate['DATE']
        timestr = self.tupdate['TIME']
        self.date.configure(text=datestr, font=self.fn0, bg='#011239', fg='white')
        self.time.configure(text=timestr, font=self.fn0, bg='#011239', fg='white')
        self.CTRLi = ImageTk.PhotoImage(Image.open(self.iupdate['CTRL']))
        self.CTRL.configure(image=self.CTRLi)
        self.ctrl1 = self.iupdate['CTRL']
        if (self.ctrl0 == './images/MANU.gif') and (self.ctrl1 == './images/AUTO.gif') and self.pop3active:
            self.popup3()
        self.ctrl0 = self.ctrl1


    def dashboard_changes(self):
    	self.update_dash_IR()
    	self.update_dash_MO()
    	self.update_dash_INDI()
    	#dash MBOX - will deal with this later


    def update_dash_IR(self):
    	#dash IR
    	self.LIRi = ImageTk.PhotoImage(Image.open(self.iupdate['LCLR']))
        #self.FIRi = ImageTk.PhotoImage(Image.open(self.iupdate['FCLR']))
        self.RIRi = ImageTk.PhotoImage(Image.open(self.iupdate['RCLR']))
        self.BIRi = ImageTk.PhotoImage(Image.open(self.iupdate['BCLR']))
        #IR sensors define labels
        self.RIR.configure(image=self.RIRi, borderwidth=0, highlightthickness=0)
        self.LIR.configure(image=self.LIRi, borderwidth=0, highlightthickness=0)
        #self.FIR.configure(image=self.FIRi, borderwidth=0, highlightthickness=0)
        self.BIR.configure(image=self.BIRi, borderwidth=0, highlightthickness=0)


    def update_dash_MO(self):
    	#dash MO
        #motors - load state 0 images
        self.LMOi = ImageTk.PhotoImage(Image.open(self.iupdate['LMO']))
        self.RMOi = ImageTk.PhotoImage(Image.open(self.iupdate['RMO']))
        self.CMOi = ImageTk.PhotoImage(Image.open(self.iupdate['CMO']))
        #motors - define labels
        self.LMO.configure(image=self.LMOi, borderwidth=0, highlightthickness=0)
        self.RMO.configure(image=self.RMOi, borderwidth=0, highlightthickness=0)
        self.CMO.configure(image=self.CMOi, borderwidth=0, highlightthickness=0)


    def update_dash_INDI(self):
    	#dash INDI
    	#indicators - load state 0  images
        self.INDi = ImageTk.PhotoImage(Image.open(self.iupdate['INDI']))
        self.DOORi = ImageTk.PhotoImage(Image.open(self.iupdate['DOOR']))
        #indicators - define labels
        self.IND.configure(image=self.INDi, borderwidth=0, highlightthickness=0)
        self.DOOR.configure(image=self.DOORi, borderwidth=0, highlightthickness=0)


    def update_sensor_icons(self):
    	#sensor icon changes
        self.battery_i = ImageTk.PhotoImage(Image.open(self.iupdate['BAT']))
        self.comb_i = ImageTk.PhotoImage(Image.open(self.iupdate['CMB']))    	
       	self.batteryi.configure(image=self.battery_i, bg='#011239', borderwidth=0, highlightthickness=0) #from volie
        self.combi.configure(image=self.comb_i, bg='#011239', borderwidth=0, highlightthickness=0) #from current


    def update_sensor_values(self):
    	self.speed.configure(text=self.tupdate['SPD'], font=self.fn0, bg='#011239', fg='white') #from GPS
        self.battery.configure(text=self.tupdate['BAT'], font=self.fn0, bg='#011239', fg='white') #from volie
        self.comb.configure(text=self.tupdate['CMB'], font=self.fn0, bg='#011239', fg='white') #from current
        self.temp.configure(text=self.tupdate['TMP'], font=self.fn0, bg='#011239', fg='white') #from humidity sensor
        self.humid.configure(text=self.tupdate['HUM'], font=self.fn0, bg='#011239', fg='white') #from humidity sensor
        self.vol.configure(text=self.tupdate['VOL'], font=self.fn0, bg='#011239', fg='white') #from internal IR


    def update_clearance_values(self):
        #obstacles - update values
        self.front.configure(text=self.tupdate['FDIST'], font=self.fn0, bg='#011239', fg='white')
        self.left.configure(text=self.tupdate['LDIST'], font=self.fn0, bg='#011239', fg='white')
        self.right.configure(text=self.tupdate['RDIST'], font=self.fn0, bg='#011239', fg='white')
        self.rear.configure(text=self.tupdate['BDIST'], font=self.fn0, bg='#011239', fg='white')


    def update_spatial_data(self):
        #spatial - update values - need to write these into the honu message
        self.lat.configure(text=self.tupdate['LAT'], font=self.fn0, bg='#011239', fg='white') 
        self.lon.configure(text=self.tupdate['LON'], font=self.fn0, bg='#011239', fg='white') 
        self.alt.configure(text=self.tupdate['ALT'], font=self.fn0, bg='#011239', fg='white') 
        self.vn.configure(text=self.tupdate['VNODE'], font=self.fn0, bg='#011239', fg='white')
        self.rn.configure(text=self.tupdate['RNODE'], font=self.fn0, bg='#011239', fg='white')
        self.bear = ImageTk.PhotoImage(Image.open('./images/CPS-X.gif').convert('RGBA').rotate(float(self.tupdate['BEAR']))) #-22.5 will be angle variable
        self.cps.configure(image=self.bear, bg='#011239', borderwidth=0, highlightthickness=0)


    def update_footer(self):
        self.outstr = helper.formatcount(self.outcount)
        self.instr = helper.formatcount(self.incount)
        self.datastr = helper.formatcount2(self.datacount)
        #self.pingtime = helper.calcping(self.outtime, self.intime)
    	self.sessionstr = '  Hostname: ' + self.hostname + '  | Host Address: ' + self.hostaddress + '  | Remote: ' + self.remotename + '  | Remote Address: ' + self.remoteaddress + '  | Sent: ' + str(self.outstr) + '  | Received: ' + str(self.instr) + '  | Data Exchanged: ' + str(self.datastr) #+ '  | Ping Time: ' + str(self.pingtime)
    	self.session.configure(text=self.sessionstr, font=self.fn0, bg='#011239', fg='white')


    def raise_frame(self, frame): #GUI Specific
        frame.tkraise()


    def plot_points(self, path, location): 
        x = []
        y = []
        for point in path:
            (lon, lat) = (point.imag, point.real)
            x.append(lat)
            y.append(lon)
        x_space = abs(max(x)-min(x))/10.0
        y_space = abs(max(y)-min(y))/10.0
        x_l = min(x)-x_space
        x_h = max(x)+x_space
        y_l = min(y)-y_space
        y_h = max(y)+y_space 
        f = Figure(figsize=(4.15, 4.15), dpi=100)
        a = f.add_subplot(111, axisbg='#FFF5E5')
        a.scatter(x,y,color='blue')
        a.scatter(x[-1],y[-1],color='red', linewidth=1)
        a.scatter(x[0],y[0],color='green', linewidth=1)
        a.plot(x, y,color='black')
        a.set_xlim([x_l,x_h])
        a.set_ylim([y_l,y_h])
        #a.set_xlabel('LONGITUDE')
        #a.set_ylabel('LATITUDE')
        a.set_xticks([])
        a.set_yticks([])
        a.grid(True)
        #f.tight_layout()
        canvas = FigureCanvasTkAgg(f, master=location)
        canvas.get_tk_widget().grid(row=0, column=0, sticky='NESW')


    def cool_plot(self, location):
        fig = plt.figure(figsize=(5,4.5), dpi=100)#figsize=(4.5, 4.15), dpi=100)
        x = np.arange(0.0, 2.5, 0.01)                           #these
        y = np.sin(2*np.pi*x)# + 0.5*np.random.randn(len(x))     #should be
        z = np.cos(2*np.pi*x)# + 0.5*np.random.randn(len(x))     #actual values at come point
        self.pfont = {'fontname':'segoe ui', 'size':10}
        ax = fig.add_subplot(111)#, axisbg='#FFF5E5')
        ax.plot(x, y, color='black', linewidth=0.5, label='honu1')
        ax.plot(x, z, color='blue', linewidth=0.5, label='honu2')
        ax.legend(loc='upper left', prop={'size':8})
        ax.set_ylim(-2, 2)
        ax.set_xlim(0,10.0)
        ax.set_xlabel('TIME', **self.pfont)
        ax.set_ylabel('VALUE', **self.pfont)
        ax.tick_params(axis='both', which='major', labelsize=8)
        ax.tick_params(axis='both', which='minor', labelsize=8)
        #ax.grid(True)
        fig.tight_layout()
        zoom = 1.0 #goes to 10
        canvas = FigureCanvasTkAgg(fig, master=location)
        canvas.get_tk_widget().grid(row=0, column=0, columnspan=3, sticky='NESW')
        self.cool_plot_elements = [zoom, ax, canvas, x]
        self.zoom_out = tk.Button(location, text=' - ',  font=self.fn2, relief='flat', command=lambda:self.zooming(direction='out'))#, bg='black', fg='white')
        self.zoom_in = tk.Button(location, text=' + ',  font=self.fn2, relief='flat', command=lambda:self.zooming(direction='in'))#, bg='black', fg='white')
        self.pan = tk.Scale(location, from_=0, to=100, orient=tk.HORIZONTAL, length=400, sliderrelief=tk.FLAT, highlightthickness=5, showvalue=False, sliderlength=400, command=self.panning)
        self.pan.set(50)
        self.zoom_out.grid(row=1, column=0, sticky='NESW')
        self.pan.grid(row=1, column=1, sticky='NESW')
        self.zoom_in.grid(row=1, column=2, sticky='NESW')


    def panning(self, event):
        self.zooming()


    def zooming(self, direction='none'):
        (zoom, ax, canvas, x) = (self.cool_plot_elements[0], self.cool_plot_elements[1], self.cool_plot_elements[2], self.cool_plot_elements[3])
        if (direction == 'in') and (zoom < 16):                
            zoom += 1.0
        elif (direction == 'out') and (zoom > 1):
            zoom += -1.0
        width = max(x)
        zoomwidth = width/zoom
        mid = width*self.pan.get()/100
        if min(x)>mid-zoomwidth:
            ax.set_xlim(min(x), zoomwidth)
        elif max(x)<mid+zoomwidth:
            ax.set_xlim(max(x)-zoomwidth, max(x))
        else:
            ax.set_xlim(mid-zoomwidth/2.0, mid+zoomwidth/2)
        canvas.draw()
        self.pan.config(sliderlength=int(400/zoom))
        self.cool_plot_elements = [zoom, ax, canvas, x]


    def play(self, path, extra):
        if self.Play:
            Play(path, extra)

    def init_control_screen(self):
        """Initializes the main menu screen"""
        #initialize values
        self.comb_state = False
        self.door_state = False
        self.e_stop_state = False
        self.pivot_state = False
        self._turn = None
        self._thrust = None

        #declare widgets
            #header
        self.control_exit_btn = tk.Button(self.fr8, font=self.fn0, relief='flat', bg='black', command=lambda:self.raise_frame(self.fr7))
        self.control_exit_btn.config(image=self.l_arrow)
        self.control_label = tk.Label(self.fr8, text='HONU REMOTE CONTROL', font=self.fn2, bg='black', fg='white')

        	#movement
        self.steering = tk.Scale(self.fr8, from_=-1, to=1, orient=tk.HORIZONTAL, length=250, sliderrelief=tk.FLAT, highlightthickness=5, showvalue=False, command=self.turning)
        self.thrust = tk.Scale(self.fr8, from_=-80, to=80, orient=tk.VERTICAL, length=250, sliderrelief=tk.FLAT, highlightthickness=5, command=self.thrusting)

        self.steering_L = tk.Label(self.fr8, text='L', font=self.fn0, bg='#000000', fg='#FFFFFF')
        self.steering_R = tk.Label(self.fr8, text='R', font=self.fn0, bg='#000000', fg='#FFFFFF')
        self.thrust_F = tk.Label(self.fr8, text='F', font=self.fn0, bg='#000000', fg='#FFFFFF')
        self.thrust_N = tk.Label(self.fr8, text='N', font=self.fn0, bg='#000000', fg='#FFFFFF')
        self.thrust_R = tk.Label(self.fr8, text='R', font=self.fn0, bg='#000000', fg='#FFFFFF')

        self.pivot_btn = tk.Button(self.fr8, text='PIVOT', font=self.fn0, bg='#DB4437', fg='#FFFFFF', relief='flat', command=lambda:self.toggle_pivot())

        	#comb and door
        self.comb_btn = tk.Button(self.fr8, text='COMB', font=self.fn0, bg='#DB4437', fg='#FFFFFF', relief='flat', command=lambda:self.toggle_comb())
        self.door_btn = tk.Button(self.fr8, text='DOOR', font=self.fn0, bg='#DB4437', fg='#FFFFFF', relief='flat', command=lambda:self.toggle_door())

        	#e-stop
        self.e_stop_btn = tk.Button(self.fr8, text='STOP\n(LOCK)', font=self.fn0, bg='#DB4437', fg='#FFFFFF', relief='flat', command=lambda:self.estop())

        #apply spacing
        self.fr8.rowconfigure(1, pad=80)
        self.fr8.columnconfigure(2, pad=180)

        #grid widgets
            #header
        self.control_exit_btn.grid(row=0, column=0, sticky='NWS')
        self.control_label.grid(row=0, column=1, columnspan=10, sticky='NEWS', ipadx=500)

        	#movement
        self.steering.grid(row=2, column=3, columnspan=3, sticky='EW')
        self.thrust.grid(row=4, column=4, rowspan=5, sticky='NS')

        self.steering_L.grid(row=2, column=2, ipadx=10, ipady=10, sticky='SE')
        self.steering_R.grid(row=2, column=6, ipadx=10, ipady=10, sticky='SW')
        self.thrust_F.grid(row=4, column=5, ipadx=10, ipady=10, sticky='W')
        self.thrust_N.grid(row=6, column=5, ipadx=10, ipady=10, sticky='W')
        self.thrust_R.grid(row=8, column=5, ipadx=10, ipady=10, sticky='W')

        self.pivot_btn.grid(row=1, column=4, ipadx=10, ipady=10)

        	#comb and door
        self.comb_btn.grid(row=4, column=2, sticky='E', ipadx=10, ipady=10)
        self.door_btn.grid(row=4, column=6, sticky='W', ipadx=10, ipady=10)

        	#e-stop
        self.e_stop_btn.grid(row=6, column=6, rowspan=3, ipadx=10, ipady=10, sticky='W')


    def turning(self, event):
        if self._turn:
            self.fr8.after_cancel(self._turn)
        self._turn = self.fr8.after(5, self.update_turn)
    
    def thrusting(self, event):
        if self._thrust:
            self.fr8.after_cancel(self._thrust)
        self._turn = self.fr8.after(5, self.update_thrust)
         
                       
    def update_turn(self):
        self.update_thrust()

    def update_thrust(self):
        thrust = self.thrust.get()
        turn = self.steering.get()
        output = int(1500-500*thrust/100.0)
        if output > 1999:
            output = 1999
        if (thrust != 0) and (turn == 0): #forward and backwards at same speed
            l_out = output + 1050
            r_out = 3500 - (output-1500)
            self.send_command(l_out)
            self.send_command(r_out)
        elif (thrust != 0) and (turn != 0) and (self.pivot_state == False):
            if (output != 1500):
                if turn > 0: #right turn - left wheel moves, right wheel stops
                    self.send_command(3500)
                elif turn < 0: #left turn - right wheel moves, left wheel stops
                    self.send_command(2500)
        elif (thrust != 0) and (turn != 0) and (self.pivot_state == True):
            if (output != 1500):
                if turn > 0: #right turn - left wheel moves, right wheel reverse
                    r_out = 3500 + (output - 1500)
                    self.send_command(r_out)
                elif turn < 0: #left turn - right wheel moves, left wheel reverse
                    l_out = 2500 - (output - 1500)
                    self.send_command(l_out)
        else:
            self.send_command(1500)
            

    def toggle_pivot(self):
	if self.pivot_state == False:
	    self.pivot_state = True
	    self.pivot_btn.configure(bg='#33B679')
            print 'pivoting'
        elif self.pivot_state == True:
	    self.pivot_state = False
	    self.pivot_btn.configure(bg='#DB4437')
            print 'no pivot'


    def toggle_comb(self):
	if self.comb_state == False:
	    self.comb_state = True
	    self.comb_btn.configure(bg='#33B679')
	    print 'comb on'
	    output = 4350
	    self.send_command(output)
        elif self.comb_state == True:
	    self.comb_state = False
	    self.comb_btn.configure(bg='#DB4437')
	    print 'comb off'
	    output = 4500
	    self.send_command(output)

	
    def toggle_door(self):
	if self.door_state == False:
	    self.door_state = True
	    self.door_btn.configure(bg='#33B679')
	    print 'door open'
	    output = 5999
	    self.send_command(output)
	elif self.door_state == True:
	    self.door_state = False
	    self.door_btn.configure(bg='#DB4437')
	    print 'door closed'
	    output = 5000
	    self.send_command(output)
	

    def estop(self):
	if self.e_stop_state == False:
	    self.e_stop_state = True
	    self.e_stop_btn.configure(bg='#33B679')
	    print 'emergency stop engaged'
	    output = 6000
	    self.send_command(output)
	elif self.e_stop_state == True:
	    self.e_stop_state = False
	    self.e_stop_btn.configure(bg='#DB4437')
	    print 'emergency stop disengaged'


    def send_command(self, code):
        '''Sends command to Honu'''
        sleep(0.01)
        send = {}
        send['MSG'] = 'SER'
        send['CMD'] = str(code)+'\n'
        self.tell_honu(str(send))
        

app=App()