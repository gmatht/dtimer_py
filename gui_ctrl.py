# See: https://stackoverflow.com/questions/434597/open-document-with-default-os-application-in-python-both-in-windows-and-mac-os

import os
import ctypes
import pyautogui

if os.name=='nt':
    import pygetwindow as gw
else:
    import pywinctl as gw

def ui_open(filepath):
    if platform.system() == 'Darwin':       # macOS
        subprocess.call(('open', filepath))
    elif platform.system() == 'Windows':    # Windows
        os.startfile(filepath)
    else:                                   # linux variants
        subprocess.call(('xdg-open', filepath))

###### Get Window Title ################
if os.name=='nt':
    from ctypes import wintypes, windll, create_unicode_buffer
    user32 = windll.user32

    def getForegroundWindowTitle():
        return gw.getActiveWindowTitle()

    bad_hwnd=0
    def store_fg(bad=False):
        global last_hwnd, bad_hwnd
        if bad:
            bad_hwnd=gw.getActiveWindow()
        else:
            hwnd = gw.getActiveWindow()
            if bad_hwnd!=hwnd:
                last_hwnd=gw.getActiveWindow()


    def topmost(root):
        root.attributes("-topmost", True)
        handle = root.frame()
        user32.SetWindowPos(handle, -1, 0, 0, 110, 110, 0x003)
        #recover_old_process(0x003)

    def unfocus(root):
        """
        Unfocuses the timer window and returns focus to the previously active window.
        Also ensures the timer window stays topmost by calling topmost() function.
        """
        global last_hwnd
        try:
           last_hwnd.activate()
        except:
           pass
        #Windows tends to forget this is meant to be above Taskbar
        #Lets remind windows occasionally
        topmost(root)
        root.after(10, topmost(root))
else:

    def unfocus(tk):
            return
            #On X11 we declare the window as being a dock and the WM will unfocus for us
            root=tk.master
            root.withdraw()
            root.deiconify()
            root.attributes("-topmost", True)

    def store_fg(bad=False):
        return

    #Instead of the next hundred odd lines, we could just do this. But it is not "Efficient"
    #def getForegroundWindowTitle():
    #    return exec_cmd("xdotool getwindowfocus getwindowname")

    from contextlib import contextmanager
    import Xlib
    import Xlib.display

    # Connect to the X server and get the root window
    xldisp = Xlib.display.Display()
    xlroot = xldisp.screen().root

    # Prepare the property names we use so they can be fed into X11 APIs
    NET_ACTIVE_WINDOW = xldisp.intern_atom('_NET_ACTIVE_WINDOW')
    NET_WM_NAME = xldisp.intern_atom('_NET_WM_NAME')  # UTF-8
    WM_NAME = xldisp.intern_atom('WM_NAME')           # Legacy encoding

    last_seen = { 'xid': None, 'title': None }

    @contextmanager
    def window_obj(win_id):
        """Simplify dealing with BadWindow (make it either valid or None)"""
        window_obj = None
        if win_id:
            try:
                window_obj = xldisp.create_resource_object('window', win_id)
            except Xlib.error.XError:
                pass
        yield window_obj

    def get_active_window():
        """Return a (window_obj, focus_has_changed) tuple for the active window."""
        win_id = xlroot.get_full_property(NET_ACTIVE_WINDOW,
                                        Xlib.X.AnyPropertyType).value[0]

        focus_changed = (win_id != last_seen['xid'])
        if focus_changed:
            with window_obj(last_seen['xid']) as old_win:
                if old_win:
                    old_win.change_attributes(event_mask=Xlib.X.NoEventMask)

            last_seen['xid'] = win_id
            with window_obj(win_id) as new_win:
                if new_win:
                    new_win.change_attributes(event_mask=Xlib.X.PropertyChangeMask)

        return win_id, focus_changed

    def _get_window_name_inner(win_obj):
        """Simplify dealing with _NET_WM_NAME (UTF-8) vs. WM_NAME (legacy)"""
        for atom in (NET_WM_NAME, WM_NAME):
            try:
                window_name = win_obj.get_full_property(atom, 0)
            except UnicodeDecodeError:  # Apparently a Debian distro package bug
                title = "<could not decode characters>"
            else:
                if window_name:
                    win_name = window_name.value
                    if isinstance(win_name, bytes):
                        # Apparently COMPOUND_TEXT is so arcane that this is how
                        # tools like xprop deal with receiving it these days
                        win_name = win_name.decode('latin1', 'replace')
                    return win_name
                else:
                    title = "<unnamed window>"

        return "{} (XID: {})".format(title, win_obj.id)

    def get_window_name(win_id):
        """Look up the window name for a given X11 window ID"""
        if not win_id:
            last_seen['title'] = "<no window id>"
            return last_seen['title']

        title_changed = False
        with window_obj(win_id) as wobj:
            if wobj:
                win_title = _get_window_name_inner(wobj)
                title_changed = (win_title != last_seen['title'])
                last_seen['title'] = win_title

        return last_seen['title'], title_changed

    def getForegroundWindowTitle():
        try:
            return (get_window_name(get_active_window()[0])[0])
        except:
            #Doesn't seem to work in LXDE
            return "ERROR"

######### IDLE TIME ##################
if os.name == 'nt':
    from ctypes import Structure, windll, c_uint, sizeof, byref
    class LASTINPUTINFO(Structure):
        _fields_ = [
            ('cbSize', c_uint),
            ('dwTime', c_uint),
        ]

    def get_idle_duration():
        lastInputInfo = LASTINPUTINFO()
        lastInputInfo.cbSize = sizeof(lastInputInfo)
        windll.user32.GetLastInputInfo(byref(lastInputInfo))
        millis = windll.kernel32.GetTickCount() - lastInputInfo.dwTime
        return millis / 1000.0

else:
    try:
        from idle_time import IdleMonitor

        monitor = IdleMonitor.get_monitor()
        monitor.get_idle_time()
        def get_idle_duration():
            return monitor.get_idle_time()

    except:
        class XScreenSaverInfo( ctypes.Structure):
            """ typedef struct { ... } XScreenSaverInfo; """
            _fields_ = [('window',      ctypes.c_ulong), # screen saver window
                        ('state',       ctypes.c_int),   # off,on,disabled
                        ('kind',        ctypes.c_int),   # blanked,internal,external
                        ('since',       ctypes.c_ulong), # milliseconds
                        ('idle',        ctypes.c_ulong), # milliseconds
                        ('event_mask',  ctypes.c_ulong)] # events

        try:
            xlib = ctypes.cdll.LoadLibrary( 'libX11.so')
        except:
            xlib = ctypes.cdll.LoadLibrary( 'libX11.so.6')
        xlib.XOpenDisplay.argtypes = [ctypes.c_char_p]
        xlib.XOpenDisplay.restype = ctypes.c_void_p  # Actually, it's a Display pointer, but since the Display structure definition is not known (nor do we care about it), make it a void pointer

        xlib.XDefaultRootWindow.argtypes = [ctypes.c_void_p]
        xlib.XDefaultRootWindow.restype = ctypes.c_uint32

        xss = ctypes.cdll.LoadLibrary( 'libXss.so.1')
        xss.XScreenSaverQueryInfo.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.POINTER(XScreenSaverInfo)]
        xss.XScreenSaverQueryInfo.restype = ctypes.c_int

        DISPLAY=os.environ['DISPLAY']
        xdpy = xlib.XOpenDisplay(None)
        xroot = xlib.XDefaultRootWindow( xdpy)
        xss.XScreenSaverAllocInfo.restype = ctypes.POINTER(XScreenSaverInfo)
        xss_info = xss.XScreenSaverAllocInfo()
        def get_idle_duration():
            global xss, xroot, xss_info
            xss.XScreenSaverQueryInfo( xdpy, xroot, xss_info)
            millis = xss_info.contents.idle
            #millis = int(exec_cmd("xprintidle"))
            return millis / 1000.0
########### END IDLE TIME ################

### END IMPORTS AND COMPATIBILITY CODE ###

### GUI CODE ###

from tkinter import ttk
class VerticalScrolledFrame(ttk.Frame):
    """A pure Tkinter scrollable frame that actually works!
    * Use the 'interior' attribute to place widgets inside the scrollable frame.
    * Construct and pack/place/grid normally.
    * This frame only allows vertical scrolling.
    """
    def __init__(self, parent, *args, **kw):
        ttk.Frame.__init__(self, parent, *args, **kw)

        # Create a canvas object and a vertical scrollbar for scrolling it.
        vscrollbar = ttk.Scrollbar(self, orient=VERTICAL)
        vscrollbar.pack(fill=Y, side=RIGHT, expand=FALSE)
        canvas = tk.Canvas(self, bd=0, highlightthickness=0,
                           yscrollcommand=vscrollbar.set)
        canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
        vscrollbar.config(command=canvas.yview)

        # Reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # Create a frame inside the canvas which will be scrolled with it.
        self.interior = interior = ttk.Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor=NW)

        # Track changes to the canvas and frame width and sync them,
        # also updating the scrollbar.
        def _configure_interior(event):
            # Update the scrollbars to match the size of the inner frame.
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # Update the canvas's width to fit the inner frame.
                canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # Update the inner frame's width to fill the canvas.
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)