#Optional Shebang for Linux (Might confuse Windows)
#!/usr/bin/env python3

import os
import gui_ctrl
### CONFIG ###

#Pomodero timer
TIME_WORK=10
TIME_PLAY=2

#Doom Clock
MIN_ORANGE=30
MIN_RED=10

LOG_TIME=True # Write time information to LOG file
ALSO_LOG_PAUSE=True # Also log while not recording billable time

# Video recording settings
VIDEO_OUTPUT_DIR = "recordings"  # Directory to save video recordings
VIDEO_FPS = 8 # Frames per second for video recording
# Note: We can't record faster than a couple of frames per second

DAT_EXTENTIONS=True # DataAnnotation Tech Specific Features
if os.name == 'nt':
    DAT_BROWSER="Microsoft​ Edge"
else:
    DAT_BROWSER="Mozilla Firefox"

GUI_TITLE="DTimer : FOREGROUND"

### END CONFIG ###

# Table of Contents:
#   CONFIG (see above: the obvious stuff to change)
#   HELP TEXT
#   IMPORTS AND COMPATIBILITY CODE
#   GUI CODE

HELP_TEXT="""
DTimer was designed to be used as a timer for work,
Specifically for Data Annotation Tech.

Created by: John McCabe-Dansted (and code snippets from StackOverflow)
License: CC BY-SA 4.0 https://creativecommons.org/licenses/by-sa/4.0/
Version: 0.92

If you want to work for DAT you can use my referral code:
2ZbHGEA

New in 0.92: Reset Time option and Record Video (No Audio) feature added.
New in 0.91: Drag and Drop Screenshot menu item added.
New in 0.9: Better Linux support, autoclick DAT logo to get doomtime
New in 0.8: Support Wayland? Switch to DataAnnotation Window.
New in 0.7: Move old GUI to 0,0 if started again
New in 0.6: DAT_EXTENSIONS (Enter Work Time) and LOG_TIME
New in 0.5: UI Enhancements, Doom Clock supports <1hr too.
New in 0.4: Removed Linux dependancy on Unifont
New in 0.3: Tested and fixed install on Ubuntu
New in 0.2: Basic Linux Support and offers to download missing files
  - What works in Linux may depend on your window manager

TODO: Support MacOS, Reduce size of logs.
Bug:  Sometimes the GUI disapears behind the taskbar.
      Set TaskBar to autohide or open log/dtimer_TIMESTAMP.tsv
      If you run it again, the old process should reappear at 0,0

--------------------------------------------

Features:
- 3 Clocks:
    * Billable Minutes
    * Doom Clock (Countdown to Deadline)
    * Wall Clock (Current Time)
- Pomodoro (Button turns red when work/play time is up)
- Record Time each Windows spends in the Foreground
    * Recorded as IDLE if the user is away for 1+ minutes
- Record Video (No Audio): Capture screen activity without sound

---------------------------------------------

Right Click Menu:
- Copy: Foreground Window Times
- View Log: Open the time tracking log file
- Fix Time: Adjust which window titles are billable
- Doom ^A^C: Copy All Text, Initialize Doom Clock from Clipboard
- Doom Picker: Manually set Deadline
- Screenshot: Take a screenshot
- Record Video: Start/stop screen recording (no audio)
--------------------------------------------
- Reset Time: Reset elapsed time counter to zero
- Restart: Set Billable time etc. to Zero
- Quit: Stop This program
--------------------------------------------
- Help: Show This Help
"""

PAUSE_SYMBOL="\u23F8" # Unicode for pause symbol
RECORD_SYMBOL="\u23FA" # Unicode for record symbol

### BEGIN IMPORTS AND COMPATIBILITY CODE ###

import os, sys, re, shutil, glob
from tkinter import ttk
from datetime import datetime
from tkinter import ttk
import queue

import subprocess, os, platform

def close_log():
    if LOG_TIME:
        log_file.close()
        os.system("gzip " + log_fname)
if LOG_TIME:
    LOG_PATH = 'log'
    if not os.path.exists(LOG_PATH):
        os.makedirs(LOG_PATH)
    timestamp=datetime.now().strftime("%Y%H%M%S")
    log_fname=os.path.join('log', f'dtimer_{timestamp}.tsv')
    log_file=open(log_fname, "a", encoding="utf-8")

def replace_last_occurrence(s, old, new):
    # Find the last occurrence of the substring
    pos = s.rfind(old)
    if pos == -1:
        return (-1,s)  # Substring not found, return the original string
    # Replace the last occurrence
    return (pos, s[:pos] + new + s[pos + len(old):])

def venv_restart():
    #vpython=sys.executable
    #os.execv(vpython, [vpython] + sys.argv)
    #return

    vpython=os.path.expanduser('~/.virtualenvs/dtimer.venv/bin/python3')
    print( "vpython: " , vpython)
    if os.path.exists(vpython):
        print ("Exists!")
        if sys.executable != vpython:
          os.execv(vpython, [vpython] + sys.argv)

venv_restart()

def restart():
    close_log()
    #venv_restart()
    #os.execv(sys.executable, [sys.executable] + sys.argv)
    os.execl(sys.executable, 'python', __file__, *sys.argv[1:])
    exit()

SCALE_FACTOR=1

#Define an 'xterm -e' like command.
#WARNING: It doesn't escape double quotes (")
if os.name=='nt':
    def xterm(cmd, confirm=None):
        c=cmd
        if confirm:
            c="set /p DUMMY=" + re.escape(confirm.replace("\n", " ")) + " & " + c
        c="start /wait cmd /k \"" +\
            c + " && set /p DUMMY=Close this window to continue...\""
        os.system(c)
else:
    def xterm(cmd, confirm=None):
        #print(f"'{cmd}' '{confirm}'")

        #c='( '+cmd+' )'
        #if confirm:
            #c="echo " + confirm.replace("\n", " ").replace("'", "\\'").replace("(", "\\()").replace(")", "\\)") + " && read _ && " + c
        #    c="echo " + confirm.translate(str.maketrans("\n'\"()", "     ")) + " && read _ && " + c
        #First we try to start a new $TERM instance. This is the terminal that
        #the user is using now, maybe it is their default terminal.
        #Failing that we try a bunch of random terminals that might be
        #available (Including a number of ones popular on MacOS although
        #we do not support MacOS yet). The first one found will be used.
        #If we do not find a terminal the user has, we just use bash. This
        #doesn't allow us to pop up a new window. However it is an OK
        #workaround for things like WSL that may not have an native terminal.

        #c="`which $TERM xfce4-terminal rxvt foot kitty konsole xterm gnome-terminal eterm urxvt gnome-terminal Alacritty alacritty warp hyper iterm2 terminal bash | head -n 1 | sed 's/bash/bash -c'/` -e \"" +\
        #      c + " ; echo Close this window to continue ; read _\""

        #Nah forget it, just use bash for everything

        if confirm:
            print(confirm)
            print("INSTALL COMMAND:" + cmd)
            print("Press Y[Enter] to install, or any other key to quit")
            if input().lower()!='y':
                quit()
        os.system(cmd)

#Try to import modules, offer to install them if it fails
#TODO: Test these actually work on a fresh install
if os.name != 'nt':
    try:
        import tkinter as tk
    except:
        xterm("sudo apt update; sudo apt install python3-tk", "DTimer needs tkinter to run.")
try:
    import tkinter as tk
    from tkinter import BooleanVar, Checkbutton, font, RIGHT, Menu, messagebox
    from collections import defaultdict
    from datetime import datetime
    from tkinter.constants import VERTICAL, LEFT, BOTH, RIGHT, NW, Y,FALSE, TRUE
    from threading import Thread

    import pyautogui
    if os.name=='nt':
        import pygetwindow as gw
    else:
        import pywinctl as gw

    #Window sometimes gets lost on windows, so move them to the top
    import ctypes
    SCALE_FACTOR = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
    move_y=0
    for w in gw.getWindowsWithTitle(GUI_TITLE):
        w.moveTo(0, move_y)
        move_y+=40*SCALE_FACTOR

    ### For Doom Clock ###
    import time
    from tktimepicker import AnalogPicker, constants

    from time import sleep

    # For video recording
    import cv2
    import numpy as np
    import mss

except ImportError as e:
    pips='datetime tktimepicker pyautogui collection pyautogui opencv-python numpy mss'
    if os.name=='nt':
        pips='pygetwindow ' + pips
    else:
        pips='idle-time pywinctl ' + pips
    #else:
    #    pips='contextlib ' + pips
    #pip has a stupid default many packages need an alternative timeout. None of the packages we will install, but lets be safe.
    #guess_conda_path=os.path.expandvars(r"%USERPROFILE%\anaconda3\condabin\conda.bat")
    pip1=os.path.expandvars(r"%USERPROFILE%/anaconda3/Scripts/pip.exe")
    (pos2,pip2)=replace_last_occurrence(sys.executable, 'pythonw', 'pip')
    if pos2<0: (pos2,pip2)=replace_last_occurrence(sys.executable, 'python', 'pip')
    msg = repr(e) + "\nWe need all of the following modules:\n" + pips + ".\n"
    #msg =+ " DTimer will quit if any modules are missing.\n"

    #Conda makes it hard to find packages, just use pip
    pip_cmd=''
    for i in range(2):
        if shutil.which('pip'):   pip_cmd="pip" #was x
        elif shutil.which('pip'):    pip_cmd="pip"
        elif shutil.which('pip3'): pip_cmd="pip3"
        elif pos2 >= 0 and os.path.exists(pip2): pip_cmd=pip2
        elif os.path.exists(pip1): pip_cmd=pip1
        else:
            if os.name!='nt' and shutil.which('apt'):
                #PIP insists on building PIL from source, so we need libjpeg-dev. I guess we don't need python3-pil?
                pip_cmd="sudo add-apt-repository universe ; sudo apt update && ( sudo apt install python3-pip python3-pil libjpeg-dev ; sudo apt install python3-venv)"
                msg+="\nPress Enter to install pip now, or close the window to quit."
                xterm(pip_cmd, msg)
                continue

            msg +=  "\nWe cannot find Pip. Please install pip or the modules and try again."
            xterm("echo bye", msg)
            quit()
        break

    if not shutil.which('ensurepip'):
        os.system("sudo apt install python3-venv")

    if os.name != 'nt':
        if os.system("python3 -m venv ~/.virtualenvs/dtimer.venv")==0:
            pip_cmd = "~/.virtualenvs/dtimer.venv/bin/pip"

    msg +=  f" Press Enter to install now({pip_cmd}), or close the window to quit."

    #pip_cmd=pip_cmd+" --default-timeout=100 install " + pips
    pip_cmd=pip_cmd + " install " + pips

    xterm(pip_cmd, msg)

    from tkinter.messagebox import askokcancel, showinfo, WARNING
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()
    install = tk.messagebox.askokcancel(
        title='Restart?',
        message="DTimer will need to restart.\nRestart (or quit)?",
        icon=WARNING)
    if not install:
        quit()
    restart()

if os.name!='nt':
    from tkinter.messagebox import askokcancel, showinfo, WARNING
    import tkinter as tk
    def support_symbol(u):
        return os.system(f"fc-list :charset={u}|grep .")==0

    #record
    if   support_symbol("26AB"): RECORD_SYMBOL="\u26AB" # ⚫︎
    elif support_symbol("23FA"): RECORD_SYMBOL="\u23FA" # ⏺︎
    elif support_symbol("25F9"): RECORD_SYMBOL="\u23F9" # ◉︎
    elif support_symbol("25CF"): RECORD_SYMBOL="\u25CF" # ●︎
    elif support_symbol("25CB"): RECORD_SYMBOL="\u25CB" # ○︎
    else: RECORD_SYMBOL="[O]"

    #pause
    if   support_symbol("23F8"): PAUSE_SYMBOL="\u23F8" # ⚫ “⏸” (U+23F8)
    elif support_symbol("9612"): PAUSE_SYMBOL="\u9612\u9612" #  “▌▌” (U+9612)
    #elif support_symbol("9613"): PAUSE_SYMBOL="\u9613\u9613" # ▍ ▍ - &#9613;
    elif support_symbol("2016"): PAUSE_SYMBOL="\u2016" # ⚫ “‖” (U+2016)
    else: PAUSE_SYMBOL="[||]"

def exec_cmd(cmd_string):
    r = os.popen(cmd_string)
    result_string = r.read()
    r.close()
    return result_string


### My Code ###

def parse_DAT(s,log_prefix=""):
        e=0
        if "DataAnnotation" not in s:
            e=1
        elif "Report Time" in s:
            e=2
        elif "Enter Work Mode" in s:
            e=3

        r=re.compile(r".*\nExpires in:[\s\n]+(?:(\d+) days? )?(?:(\d+) hours?)? ?(?:(\d+) minutes?)?\n[$]\d.*",re.MULTILINE|re.DOTALL)
        mat=r.match(s)
        d=None
        h=None
        m=None
        if mat:
            d,h,m=mat.groups()
            if not d:
                d=0
            if not h:
                h=0
            if not m:
                m=0
        ls=f"log/{log_prefix}doom-{e}"
        log=open(ls, "a", encoding="utf-8")

        log.write(f"--- {e} {d} {h} {m} --- \n")
        log.write(f"{s}\n")
        log.close()
        return (e,d,h,m)



#def init_pos():
def copy_all():
#    if os.name!='nt':
#        #pynput should work in linux, but it doesn't seem to
#        #you may have to play a bit with this to get it to work with your window manager.
#        if os.system("sleep 0.1 && xdotool key ctrl+a && sleep 1.1 && xdotool key ctrl+c")==0:
#            return
    with pyautogui.hold('ctrl'):
        pyautogui.press('a')
        pyautogui.press('c')

print (SCALE_FACTOR)

def non_blocking_messagebox(title,desc,button_label,command):
    message_window = tk.Toplevel()
    message_window.title(title)
    #message_window.geometry("300x100")

    def onpress():
        command()
        #message_window.destroy

    label = ttk.Label(message_window, text=desc)
    label.pack(pady=10, padx=10)

    close_button = ttk.Button(message_window, text=button_label, command=onpress)
    close_button.pack(pady=10)

    # Make sure the window doesn't block the main application
    #message_window.transient()  # Keep it on top of the main window
    message_window.attributes ('-topmost', True)

    return message_window

class TimeTrackerApp(tk.Toplevel):
    def __init__(self, master):
        self.master = master
        self.master.title(GUI_TITLE)
        self.master.overrideredirect(True)
        self.menu_showing=False
        if os.name != 'nt':
            self.master.wm_attributes("-type", "dock")

        self.recording = False # Recording work time (not video)
        self.last_time = time.time()
        self.toggle_time = self.last_time
        self.doom_time = 0
        self.elapsed_time = 0
        self.last_logged_hour = None  # Track the last logged hour


        # Create video output directory if it doesn't exist
        if not os.path.exists(VIDEO_OUTPUT_DIR):
            os.makedirs(VIDEO_OUTPUT_DIR)

        #SCALE_FACTOR=float(root.tk.call('tk', 'scaling'))/1.1

        ft = font.Font(family='Arial', size=16)
        self.time_label = tk.Label(master, text="00:00:00", font=ft)
        self.time_label.place(x=0,y=0)

        ft = font.Font(family='Arial', size=16)
        self.button = tk.Button(master, text=RECORD_SYMBOL, font=ft, command=self.toggle_recording)
        self.button.place(x=88*SCALE_FACTOR,y=0)

        #self.master.geometry(f"{138*scale_factor}x{42*scale_factor}")

        ft = font.Font(family='Arial', size=9)
        self.doom_label = tk.Label(master, text="00:00:00", font=ft)
        #self.doom_label.pack(padx=1,pady=0,side=tk.LEFT)
        self.doom_label.place(x=0,y=22*SCALE_FACTOR)
        self.wall_clock = tk.Label(master, text="00:00", font=ft)
        self.wall_clock.place(x=52*SCALE_FACTOR,y=22*SCALE_FACTOR)

        self.title_times = defaultdict(float)
        self.pause_times = defaultdict(float)
        self.window_time_log = defaultdict(float)  # Track time for each window title
        self.last_hour = time.time()  # Track the last time we logged the top titles

        self.master.bind("<ButtonPress-1>", self.start_move)
        self.master.bind("<ButtonRelease-1>", self.stop_move)
        self.master.bind("<B1-Motion>", self.do_move)
        self.master.bind("<Button-3>", self.do_popup)

        # Video recording variables
        self.video_thread = None
        self.is_recording_video = False
        self.video_writer = None
        self.sct = None
        self.video_start_time = None
        self.video_filename = None
        self.last_frame_time = None
        self.video_messagebox = None
        self.frame_num = 0

        t=root
        w = 133*SCALE_FACTOR #t.winfo_width() # width for the Tk root
        h = 40*SCALE_FACTOR # t.winfo_width() # height for the Tk root
        print(w,':',h)

        # get screen width and height
        ws = t.winfo_screenwidth() # width of the screen
        hs = t.winfo_screenheight() # height of the screen

        # calculate x and y coordinates for the Tk root window
        x = (ws-2)*8/10 # - 100
        y = hs - h - 4 - 8  * SCALE_FACTOR # - 100

        # set the dimensions of this timer window
        # and where it is placed
        root.geometry('%dx%d+%d+%d' % (w, h, x, y))

        m = Menu(root, tearoff=0)
        m.add_command(label="Copy", command=self.do_copy)
        m.add_command(label="View Log", command=self.view_log)
        m.add_command(label="Fix Time", command=self.fix_time)
        if DAT_EXTENTIONS:
            m.add_command(label="Doom ^A^C", command=self.do_doom)
        m.add_command(label="Doom Picker", command=self.get_time)
        m.add_command(label="Screenshot", command=self.launch_screenshot)
        m.add_command(label="Record Video", command=self.toggle_video_recording)
        if DAT_EXTENTIONS:
            m.add_separator()
            m.add_command(label="Submit", command=self.do_submit)
        m.add_separator()
        m.add_command(label="Reset Time", command=self.reset_time)
        m.add_command(label="Restart", command=restart)
        m.add_command(label="Quit", command=self.do_quit)
        m.add_separator()
        m.add_command(label="Help", command=self.do_help)
        self.popup_menu = m

        self.last_hhmm=""
        self.update_time()

        self.master.after(1, lambda: gui_ctrl.store_fg(bad=True))
        self.master.after(10, lambda: gui_ctrl.unfocus(root))

        root.update()

        #TODO: Check if this code works in NT too.
        if os.name != 'nt':
            LINE_SPACING=0.7

            tl_h=self.time_label.winfo_height()
            tl_w=self.time_label.winfo_width()
            self.time_label.place(x=0,y=tl_h*(LINE_SPACING-1)/2)
            self.button.place(x=tl_w,y=0)
            self.doom_label.place(x=0,y=tl_h*LINE_SPACING)
            self.wall_clock.place(x=tl_w-self.wall_clock.winfo_width(),y=tl_h*LINE_SPACING)
            w = tl_w + self.button.winfo_width()
            #h = (tl_h + self.doom_label.winfo_height() * LINE_SPACING)
            h = self.button.winfo_height()

            # y = hs - h - 4 * SCALE_FACTOR # - 100
            x=y=0
            root.geometry('%dx%d+%d+%d' % (w, h, x, y))


    # New method to reset time
    def reset_time(self):
        #resets all timers to 0

        self.menu_showing = False
        # Reset timers and counters
        self.elapsed_time = 0
        self.title_times = defaultdict(float)
        self.pause_times = defaultdict(float)
        self.window_time_log = defaultdict(float)
        self.last_time = time.time()
        self.toggle_time = self.last_time
        self.time_label.config(text="00:00:00")
        # Optionally reset doom time if desired
        # self.doom_time = 0

        # Log the reset if logging is enabled
        if LOG_TIME:
            log_file.write("R\tRESET\tTime counters reset\n")
            log_file.flush()

        messagebox.showinfo("Time Reset", "Time counters have been reset.")

    # New methods for video recording
    def start_video_record(self):
        #Starts capturing frames and queueing them to be encoded by another thread

        if self.is_recording_video:
            messagebox.showwarning("Already Recording", "Video recording is already in progress.")
            return

        self.popup_menu.entryconfig("Record Video", label="Stop Recording")


        # Initialize screen capture
        self.sct = mss.mss()

        #Do not store more than a second of frames, it could easily flood memory
        self.video_queue = queue.Queue(VIDEO_FPS)

        def writer_fn():
            #write frames to avi file

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            fname = f'video_{timestamp}.mp4'
            self.video_filename = os.path.join(VIDEO_OUTPUT_DIR, fname)

            # Get screen dimensions (capture primary monitor)
            monitor = self.sct.monitors[1]  # 0 is all monitors, 1 is primary

            # Set up video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            #fourcc = cv2.VideoWriter_fourcc(*'avc1')
            #Keep all calls to video_writer on the same thread.
            self.video_writer = cv2.VideoWriter(self.video_filename, fourcc, VIDEO_FPS * 1.0,
                                              (monitor["width"], monitor["height"]))

            while True:
                #Python Queues implement required locking.
                frame = self.video_queue.get()
                if frame is None:
                    return
                frame = np.array(frame)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                self.video_writer.write(frame)

            self.video_writer.release()

        self.video_thread = Thread(target=writer_fn)
        self.video_thread.start()

        start_frame_time=time.time()
        self.is_recording_video = True
        self.video_start_time = time.time()
        self.video_messagebox = non_blocking_messagebox("Video Recording",
            f"Started recording video to:\n{self.video_filename}",
            "Stop Recording",self.stop_video_record)
        self.record_video_frame()

    def stop_video_record(self):
        #Cleanup and stop recording video

        if not self.is_recording_video:
            messagebox.showwarning("Not Recording", "No video recording is in progress.")
            return

        self.video_queue.put(None)
        self.popup_menu.entryconfig("Stop Recording", label="Record Video")
        self.video_messagebox.destroy()
        self.video_messagebox = None

        self.is_recording_video = False
        self.frame_num = 0

        # Release resources
        if self.sct:
            self.sct.close()

        duration = time.time() - self.video_start_time
        mins, secs = divmod(duration, 60)
        hours, mins = divmod(mins, 60)

        messagebox.showinfo("Video Recording Stopped",
                          f"Video saved to: {self.video_filename}\n"
                          f"Duration: {int(hours):02d}:{int(mins):02d}:{int(secs):02d}")

        # Log the video recording if logging is enabled
        if LOG_TIME:
            log_file.write(f"V\tVIDEO\t{self.video_filename}\t{duration:.2f}\n")
            log_file.flush()

    def toggle_video_recording(self):
        """Start or stop video recording"""

        self.menu_showing = False

        if self.is_recording_video:
            self.stop_video_record()
        else:
            self.start_video_record()

    def record_video_frame(self):
        if not self.is_recording_video:
            self.last_frame_time=None
            return

        start_frame_time=time.time()

        deadline_s  = 1/VIDEO_FPS
        deadline_ms = int(1000*deadline_s)


        # Capture screen
        frame = self.sct.grab(self.sct.monitors[1])
        self.video_queue.put(frame)
        finish_frame_time=time.time()

        self.frame_num += 1
        next_frame_time = self.video_start_time + ( deadline_s * self.frame_num )

        ms_taken=(finish_frame_time-start_frame_time)*1000

        #uncomment to help debug time issues
        #if self.last_frame_time:
        #   total_time_between_frames=finish_frame_time-self.last_frame_time
        #   print(f"{ms_taken}ms Total:{total_time_between_frames}s Deadline:{deadline_s}s\n")

        # Schedule next frame (approximately 20 FPS)
        late = finish_frame_time - next_frame_time
        self.master.after(max(0, round(1000 * -late)), self.record_video_frame)

        if late > (deadline_s/4):
            #frame is significantly late
            num=self.frame_num
            print(f"Frame {num} late {late}s, working:{ms_taken}ms. Deadline {deadline_s}\n")

        self.last_frame_time=time.time()

    def do_quit(self):
        close_log()
        self.master.destroy()

    def view_log(self):
        self.menu_showing=False
        log_file.flush()
        ui_open(log_fname)

    def do_about(self):
        self.menu_showing=False
        tk.messagebox.showinfo(
            title="About DTimer",
            message=ABOUT_TEXT)

    def do_help(self):
        self.menu_showing=False
        tk.messagebox.showinfo(
            title="DTimer HELP",
            message=HELP_TEXT)

    def updateTime(self,t):
        (a,b,c)=t
        self.doom_time=time.time()+a*3600+b*60

    def get_time(self):
        self.menu_showing=False
        root=self.master
        top = tk.Toplevel(root)
        top.title("Set Deadline")

        time_picker = AnalogPicker(top, type=constants.HOURS24)
        time_picker.setHours(1)
        time_picker.setMinutes(0)
        time_picker.pack(expand=True, fill="both")
        ok_btn = tk.Button(top, text="Set Doom Clock", command=lambda:
                           self.updateTime(time_picker.time()))
        ok_btn.pack()

    def fix_time(self):
        self.menu_showing=False
        from tkinter import Canvas, Scrollbar, CENTER, Frame
        top = tk.Toplevel(self.master)
        top.title('Fix Billable Time')

        top.rowconfigure(0, weight=0)
        top.rowconfigure(1, weight=1)
        top.columnconfigure(0, weight=1)

        frame = VerticalScrolledFrame(top)
        frame.grid(row=1, column=0, sticky="nsew")

        times_frame = frame.interior

        col_sizes = [0,0]

        def add(key,value,default,prefix=""):
             self.category_values.append(BooleanVar())
             self.category_values[-1].set(default)
             m=value/60
             self.category_mins.append(m)
             l=Checkbutton(times_frame, text=f"{prefix} {key} ({m:.2f})", variable=self.category_values[-1], command=lambda: self.fix_time_recalc(), anchor='w',)
             col=default
             l.grid(column=col, row=col_sizes[col], sticky=tk.W,pady=0, padx=0)
             col_sizes[col]+=1

        self.category_values = []
        self.category_mins = []
        for k, v in sorted(self.title_times.items(), key=lambda item: -item[1]): add(k,v,1,RECORD_SYMBOL)
        for k, v in sorted(self.pause_times.items(), key=lambda item: -item[1]): add(k,v,0,PAUSE_SYMBOL)

        self.fix_time_label=tk.Label(top, text="")
        self.fix_HHMM_label=tk.Label(times_frame, text="")
        self.fix_time_recalc()

        col=0; self.fix_time_label.grid(column=0, row=0, sticky=tk.W,pady=0, padx=0,)
        col=1; self.fix_HHMM_label.grid(column=col, row=col_sizes[col], sticky=tk.W,pady=0, padx=0)

    def fix_time_recalc(self):
        t=0
        for i in range(len(self.category_mins)):
            t+=self.category_values[i].get()*self.category_mins[i]
        self.fix_time_label.config(text=f"Minutes: {t:.2f}" + "  [{:02d}:{:02d}]".format(*divmod(int(t), 60)))

    def do_submit(self):
        dt=datetime.now().strftime("%Y%m%d-%H%M%S")
        self.do_doom(f"submit-{dt}")
        with pyautogui.hold('ctrl'):
            pyautogui.press('f')
        pyautogui.typewrite('submit')
        pyautogui.press('enter')

    def do_doom(self, log_prefix=""):
        self.menu_showing=False
        global log_file
        gui_ctrl.unfocus(root)

        title=getForegroundWindowTitle()
        if not title.startswith("DataAnnotation"):
            for x in gw.getAllWindows():
                if x.title.startswith("DataAnnotation"):
                    x.activate()
                    time.sleep(0.01)
                    break

        title=getForegroundWindowTitle()
        if not title.startswith("DataAnnotation"):
            for win in gw.getAllWindows():
                print(win.title)
                if win.title.endswith(DAT_BROWSER):
                    print(win.title)
                    win.activate()
                    w=win
                    break

            time.sleep(.01)

            #w=gw.getActiveWindow()
            r=(w.left,w.top,w.width,64)
            #for img in ['dat_logo.png', 'dat_logo_grey.png', 'dat3.png', 'dat5.png','dat7.png']*150:
            browser=DAT_BROWSER.split()[-1]
            for img in glob.glob(f"img/{browser}/img*.png"):
            #for i in range(17):
                #img=f"img/img{i}.png"
                try:
                    x, y = pyautogui.locateCenterOnScreen(img,region=r)
                    print("point", x, y)
                    pyautogui.click(x, y)

                    break
                except:
                    time.sleep(.001)
            print(r)
        copy_all()
        time.sleep(0.1)
        s=self.master.clipboard_get()

        (e,d,h,m)=parse_DAT(s, log_prefix)

        if e==1:
            tk.messagebox.showwarning("Could not find DataAnnotation", "You do not appear to have the DataAnnotation Window in the foreground.\nUnable to check Work Mode and Deadlines.")
        elif e==2:
            tk.messagebox.showwarning("Enter Work Mode", "You appear to be on DAT's main screen. Please remember to press 'Enter Work Mode' after selecting a project.")
        elif e==3:
            tk.messagebox.showwarning("Enter Work Mode", "You do not appear to be in work mode\nPlease Enter Work Mode Now.")

        if not d is None or e==0:
            if not d:
                d=0
            if not h:
                h=0
            if not m:
                m=0
            self.doom_time=time.time()+(int(d)*24+int(h))*3600+int(m)*60
            if LOG_TIME:
                log_file.write("D\t"+str(self.doom_time)+"\n")

        if LOG_TIME:
            r=re.compile(r".*Projects\r?\n([^\n\r]*)",re.MULTILINE|re.DOTALL)
            #r=re.compile(r"Projects\r?\n(.*)",re.MULTILINE)
            mat=r.match(s)
            if mat:
                log_file.write("N\t"+mat.group(1)+"\n")

            #r=re.compile(r"Prompt ID: (.*) .Make a note of the ID",re.MULTILINE|re.DOTALL)
            #r=re.compile(r"[:] (.*) .Make a",re.MULTILINE|re.DOTALL)
            r=re.compile(r".*Prompt ID: (.*) .Make a",re.MULTILINE|re.DOTALL)
            mat=r.match(s)
            if mat:
                log_file.write("I\t"+mat.group(1)+"\n")

    def do_copy(self):
        self.menu_showing=False
        s=''
        for key,value in self.title_times.items():
            min=value/60
            s+=f"+\t{min:7.3f}\t{key}\n"
        for key,value in self.pause_times.items():
            min=value/60
            s+=f"P\t{min:7.3f}\t{key}\n"
        self.master.clipboard_clear()
        self.master.clipboard_append(s)

    def do_popup(self, event):
        m=self.popup_menu
        self.menu_showing = True
        try:
            m.tk_popup(event.x_root, event.y_root)
        finally:
            m.grab_release()

    def start_move(self, event):
        gui_ctrl.store_fg(bad=True)
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        self.x = None
        self.y = None
        gui_ctrl.unfocus(root)

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.master.winfo_x() + deltax
        y = self.master.winfo_y() + deltay
        self.master.geometry(f"+{x}+{y}")


    def toggle_recording(self):
        gui_ctrl.store_fg(bad=True)
        self.update_time()
        self.toggle_time=time.time()
        self.recording = not self.recording
        if self.recording:
            if DAT_EXTENTIONS:
                self.do_doom()
            self.button.config(text=PAUSE_SYMBOL)
        else:
            self.button.config(text=RECORD_SYMBOL)
        gui_ctrl.unfocus(root)

    def time2str(self,secs):
        minutes, seconds = divmod(secs, 60)
        hours, minutes = divmod(minutes, 60)
        return "%02d:%02d:%02d" % (hours, minutes, seconds)

    def update_time(self):
        from datetime import datetime
        global log_file
        #Move this to the top to see if it fixes the timer hiding behind the taskbar
        self.master.after(1000, self.update_time)  # Update every 1000 milliseconds
        dt = datetime.now()
        hhmm=dt.strftime("%H:%M")
        self.wall_clock.config(text=hhmm)

        #Windows tends to forget this is meant to be above Taskbar
        #Lets remind windows occasionally
        if not self.menu_showing:
            if os.name == 'nt':
                gui_ctrl.topmost(root)

        gui_ctrl.store_fg()

        ctime=dt.timestamp()

        addtime = ctime - self.last_time
        window = gui_ctrl.getForegroundWindowTitle()
        title = window if window else "NONE"

        fg='green'
        if self.doom_time > ctime:
            self.doom_label.config(text=self.time2str(self.doom_time-ctime))
            mins=(self.doom_time - ctime)/60
            if mins < MIN_ORANGE:
                fg='orange'
                if mins < MIN_RED:
                    fg='red'
        else:
            self.doom_label.config(text="00:00:00")
        self.doom_label.config(fg=fg)
        idle_duration=gui_ctrl.get_idle_duration()

        MAX_LEN = 40
        title = (title[:(MAX_LEN-3)] + '...') if len(title) > MAX_LEN else title

        if LOG_TIME:
            if self.last_hhmm != hhmm:
                self.last_hhmm=hhmm
                log_file.write("T\t"+hhmm+"\n")
            if self.recording:
                status="R"
            else:
                status="P"
            if ALSO_LOG_PAUSE or self.recording():
                log_file.write(f"{status}\t{idle_duration:.0f}\t{addtime:.4f}\t{title}\n")

        if idle_duration > 60:
            title = "IDLE"

        if self.recording:
            wanted_mins=TIME_WORK
            self.elapsed_time += addtime
            self.title_times[title] += addtime
            minutes, seconds = divmod(self.elapsed_time, 60)
            hours, minutes = divmod(minutes, 60)
            self.time_label.config(text=self.time2str(self.elapsed_time))
        else:
            wanted_mins=TIME_PLAY
            self.pause_times[title] += addtime
        period_mins=(ctime-self.toggle_time)/60
        if wanted_mins>period_mins:
            bg='lightgrey'
        else:
            bg='red'
        if TIME_WORK*TIME_PLAY:
            self.button.configure(bg=bg)

        self.last_time = ctime

        # Get the current hour
        current_hour = datetime.now().hour

        # Check if the hour has changed
        if current_hour != self.last_logged_hour:
            self.log_top_window_times()  # Log the top window times
            self.last_logged_hour = current_hour  # Update the last logged hour

    def log_top_window_times(self):
        # Sort the window titles by time spent and get the top 10
        top_titles = sorted(self.title_times.items(), key=lambda item: item[1], reverse=True)[:10]

        # Log to a file
        log_file_path = os.path.join('log', 'top_window_times.tsv')
        with open(log_file_path, 'a', encoding='utf-8') as log_file:
            log_file.write(f"Top Window Titles for the hour ending at {self.last_logged_hour}:00:\n")
            for title, time_spent in top_titles:
                minutes = time_spent / 60
                log_file.write(f"{title}: {minutes:.2f} minutes\n")
            log_file.write("\n")  # Add a newline for separation

    def launch_screenshot(self):
        self.menu_showing = False
        #Start the screenshot app in a new process to avoid mixing Tkinter with TkinterDnD
        subprocess.Popen([sys.executable, 'dnd_screenshot.py'])
        #TODO: Merge the screenshot app with the main app
        # May need to port main app (dtimer.pyw) to TkinterDnD
        # May need to check that screenshot() does not leak memory or window handles
        # then do:
        #    from dnd_screenshot import screenshot
        #    screenshot()
        # and rename main() to screenshot() in dnd_screenshot.py

root = tk.Tk()
app = TimeTrackerApp(root)
root.call('wm', 'attributes', '.', '-topmost', '1')
root.mainloop()
