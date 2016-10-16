from tkinter import *
from tkVWidgets import TimeEntry, Utils
import time
import subprocess
import configparser
import os.path
import tkinter.messagebox

class MainWindow(Frame):
    def __init__(self, master, **kwargs):
        self.master = master
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)
        Frame.__init__(self, master, **kwargs)
        self.ini_file = 'config.ini'
        self.default_time = (0, 0, 0)
        self.mode = IntVar()
        self.mode.set(1)
        self.load_from_cfg()

        self.light_blue = '#D4E0ED'
        self.dark_blue = '#B3C8DF'
        self.red = '#DFC8B3'
        master['bg'] = self.light_blue
        f = ('Helvetica', 14, NORMAL)
        Label(master, text='Выключить компьютер', font=('Helvetica', 18, NORMAL), bg=self.light_blue).pack(side=TOP, fill=X, expand=1, pady=10)

        frame = Frame(master, bg=self.dark_blue)
        frame.pack(side=TOP, padx=5)
        self.rb1 = Radiobutton(frame, text='через', variable=self.mode, value=1, font=f, bg=self.dark_blue)
        self.rb1['activebackground'] = self.dark_blue
        self.rb1.grid(row=0, column=0, sticky=W, padx=5)
        self.rb2 = Radiobutton(frame, text='в', variable=self.mode, value=2, font=f, bg=self.dark_blue)
        self.rb2['activebackground'] = self.dark_blue
        self.rb2.grid(row=1, column=0, sticky=W, padx=5)

        self.timeEntry = TimeEntry.TimeEntry(frame, font=('Helvetica', 30, NORMAL), default_time=self.default_time)
        self.timeEntry.grid(row=0, column=1, rowspan=2, padx=5)

        self.btn_start = Button(master, text='Старт', font=f, command=self.start_click, bg=self.dark_blue)
        self.btn_start.pack(side=TOP, pady=10)
        self.status = 0
        self.seconds_left = 0

    def on_close(self):
        if self.status == 1:
            if not tkinter.messagebox.askokcancel("Выход", "Запущен процесс выключения компьютера. Вы уверены, что хотите выйти?"):
                return
        self.save_to_cfg()
        self.master.destroy()

    def load_from_cfg(self):
        if os.path.isfile(self.ini_file):
            cfg = configparser.ConfigParser()
            cfg.read(self.ini_file)
            if 'Options' not in cfg.sections():
                return
            if 'Time' in cfg['Options'].keys():
                l = cfg['Options']['Time'].split(':')
                if len(l) >= 3:
                    self.default_time = (l[0], l[1], l[2])
            if 'Mode' in cfg['Options'].keys():
                if cfg['Options']['Mode'] == 'In':
                    self.mode.set(1)
                elif cfg['Options']['Mode'] == 'At':
                    self.mode.set(2)

    def save_to_cfg(self):
        cfg = configparser.ConfigParser()
        d = dict()
        d['Time'] = ':'.join([str(s).zfill(2) for s in self.timeEntry.get_time()])
        if self.mode.get() == 1:
            d['Mode'] = 'In'
        elif self.mode.get() == 2:
            d['Mode'] = 'At'
        cfg['Options'] = d
        with open(self.ini_file, 'w') as f:
            cfg.write(f)

    def apply_status(self):
        if self.status == 1:
            self.rb1['state'] = DISABLED
            self.rb2['state'] = DISABLED
            self.timeEntry['state'] = DISABLED

            self.btn_start['text'] = 'Отмена'
            self.btn_start['bg'] = self.red
        else:
            self.rb1['state'] = NORMAL
            self.rb2['state'] = NORMAL
            self.timeEntry['state'] = NORMAL

            self.btn_start['text'] = 'Старт'
            self.btn_start['bg'] = self.dark_blue

    def calc_seconds_left(self):
        hours, minutes, seconds = self.timeEntry.get_time()
        self.seconds_left = hours * 60 * 60 + minutes * 60 + seconds
        if self.mode.get() == 2:
            curr_time = time.localtime()
            curr_seconds = curr_time.tm_hour * 60 * 60 + curr_time.tm_min * 60 + curr_time.tm_sec
            if curr_seconds <= self.seconds_left:
                self.seconds_left -= curr_seconds
            else:
                self.seconds_left += (24 * 60 * 60) - curr_seconds

    def start_click(self):
        if self.status == 0:
            self.status = 1
        else:
            self.status = 0
        self.apply_status()
        if self.status == 1:
            self.calc_seconds_left()
            self.on_timer()

    def on_timer(self):
        if self.status == 0:
            return
        self.seconds_left -= 1
        if self.seconds_left <= 0:
            self.status = 0
            self.save_to_cfg()
            subprocess.call(["shutdown", "-f", "-s", "-t", "0"])
            self.quit()
        self.btn_start['text'] = 'Отмена (осталось '+ time.strftime('%H:%M:%S', time.gmtime(self.seconds_left)) + ')'
        self.timeEntry.after(1000, self.on_timer)

root = Tk()
if os.path.isfile('shutdown.ico'):
    root.iconbitmap('shutdown.ico')
mainWindow = MainWindow(root)
mainWindow.pack()
Utils.center(root)
root.resizable(0, 0)
root.title("Выключение компьютера")
root.mainloop()