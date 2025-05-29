import tkinter as tk
from tkinter import simpledialog, messagebox
from PIL import Image, ImageGrab, ImageTk
import os
import tempfile
import sys
import threading
import time
import ctypes
ctypes.windll.shcore.SetProcessDpiAwareness(1)

import platform
from tkinterdnd2 import *
try:
    from Tkinter import *
    from ScrolledText import ScrolledText
except ImportError:
    from tkinter import *
    from tkinter.scrolledtext import ScrolledText

SCALE_FACTOR=1

if os.name=='nt':
    from ctypes import windll
    SCALE_FACTOR = windll.shcore.GetScaleFactorForDevice(0) / 100

# Helper function to print event info for debugging
def print_event_info(event):
    print('Application: %s' % event.widget.winfo_toplevel().winfo_name())
    print('Widget: %s' % event.widget._name)
    print('X Origin: %d' % event.x_root)
    print('Y Origin: %d' % event.y_root)
    print('X: %d' % event.x)
    print('Y: %d\n' % event.y)

class ScreenshotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Screenshot Tool")
        #self.SCALE_FACTOR=float(self.root.tk.call('tk', 'scaling'))
        self.root.geometry("400x200")

        # Variables
        self.start_x = 0
        self.start_y = 0
        self.current_x = 0
        self.current_y = 0
        self.screenshot = None
        self.rect_id = None
        self.selection_window = None
        self.image_window = None
        self.temp_file = None
        self.temp_file_name = None
        self.countdown_window = None
        self.countdown_label = None

        # Hide the main window immediately
        self.root.withdraw()

        # Auto-start the capture process
        self.start_capture()

    def start_capture(self, delayed=False):
        # No need to iconify since the main window is already hidden
        #self.root.iconify()

        # If delayed mode, first take a full screen screenshot
        if delayed:
            self.start_countdown(5)
            return

        # Create a fullscreen transparent window for selection
        self.selection_window = tk.Toplevel(self.root)
        self.selection_window.attributes('-fullscreen', True)
        self.selection_window.attributes('-alpha', 0.3)
        self.selection_window.attributes('-topmost', True)

        # Create canvas for drawing selection rectangle
        self.canvas = tk.Canvas(self.selection_window, cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Bind mouse events
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        # Bind escape key to cancel
        self.selection_window.bind("<Escape>", lambda e: self.cancel_selection())

    def start_countdown(self, seconds=5):
        # Create countdown window
        self.countdown_window = tk.Toplevel(self.root)
        self.countdown_window.attributes('-topmost', True)

        # Center the window
        window_width = int(200 * SCALE_FACTOR)
        window_height = int(100 * SCALE_FACTOR)
        screen_width = self.countdown_window.winfo_screenwidth()
        screen_height = self.countdown_window.winfo_screenheight()
        x_coordinate = int((screen_width - window_width) / 2)
        y_coordinate = int((screen_height - window_height) / 2)
        self.countdown_window.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

        # Configure the window
        self.countdown_window.title("Countdown")
        self.countdown_window.configure(bg='black')

        # Create countdown label
        self.countdown_label = tk.Label(
            self.countdown_window,
            text=str(seconds),
            font=('Arial', 48),
            fg='white',
            bg='black'
        )
        self.countdown_label.pack(fill=tk.BOTH, expand=True)

        # Start countdown
        self.image_window.destroy()
        self.update_countdown(seconds)


    def update_countdown(self, seconds):
        #Do the actual countdown
        if seconds > 0:
            if seconds > 1:
                delay = 1000
            else:
                delay = 500
            self.countdown_label.config(text=str(seconds))
            self.countdown_window.after(delay, self.update_countdown, seconds - 1)
        else:
            # Close countdown window
            self.countdown_window.destroy()
            # Take fullscreen screenshot, but give windows some time to remove the countdown window
            time.sleep(0.5)
            self.take_fullscreen_screenshot()

    def take_fullscreen_screenshot(self):
        # Take fullscreen screenshot
        self.screenshot = ImageGrab.grab()

        # Save to temporary file
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        self.screenshot.save(self.temp_file.name)
        self.temp_file_name = self.temp_file.name
        self.temp_file.close()

        # Now start selection window to let user select a portion
        self.start_selection_on_image()

    def start_selection_on_image(self):
        # Create a fullscreen window for selection
        self.selection_window = tk.Toplevel(self.root)
        self.selection_window.attributes('-fullscreen', True)
        self.selection_window.attributes('-topmost', True)

        # Create canvas for drawing selection rectangle and display the screenshot
        self.canvas = tk.Canvas(self.selection_window, cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Display the screenshot on the canvas
        self.tk_fullscreen_image = ImageTk.PhotoImage(self.screenshot)
        self.canvas.create_image(0, 0, image=self.tk_fullscreen_image, anchor="nw")

        # Bind mouse events
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        # Bind escape key to cancel
        self.selection_window.bind("<Escape>", lambda e: self.cancel_selection())

    def on_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.rect_id = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline='red', width=2
        )

    def on_drag(self, event):
        self.current_x = event.x
        self.current_y = event.y
        self.canvas.coords(self.rect_id, self.start_x, self.start_y, self.current_x, self.current_y)

    def on_release(self, event):
        # Get the final coordinates
        x1 = min(self.start_x, self.current_x)
        y1 = min(self.start_y, self.current_y)
        x2 = max(self.start_x, self.current_x)
        y2 = max(self.start_y, self.current_y)

        # Close selection window
        self.selection_window.destroy()

        # Take the screenshot of the selected region or crop the fullscreen screenshot
        if hasattr(self, 'tk_fullscreen_image'):
            # We're working with a fullscreen screenshot, so crop it
            self.crop_screenshot(x1, y1, x2, y2)
        else:
            # We're taking a new screenshot of the selected region
            self.take_screenshot(x1, y1, x2, y2)

    def crop_screenshot(self, x1, y1, x2, y2):
        # Crop the existing screenshot
        if x2 - x1 < 1 or y2 - y1 < 1:
            messagebox.showinfo("Invalid Selection", "Please select a larger region")
            return

        #self.screenshot = self.screenshot.crop((self.scale(x1), self.scale(y1), self.scale(x2), self.scale(y2)))
        self.screenshot = self.screenshot.crop((x1, y1, x2, y2))

        # Save to temporary file
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        self.screenshot.save(self.temp_file.name)
        self.temp_file_name = self.temp_file.name
        self.temp_file.close()

        # Display the screenshot
        self.display_screenshot()

    def cancel_selection(self):
        if self.selection_window:
            self.selection_window.destroy()
        # Close the application since there's no main window to return to
        self.root.destroy()

    #def scale(self,x):
    #    return int(x*SCALE_FACTOR)

    def take_screenshot(self, x1, y1, x2, y2):
        # Ensure we have a valid selection
        if x2 - x1 < 1 or y2 - y1 < 1:
            messagebox.showinfo("Invalid Selection", "Please select a larger region")
            return

        # Capture the screenshot
        # self.screenshot = ImageGrab.grab(bbox=(self.scale(x1), self.scale(y1), self.scale(x2), self.scale(y2)))
        self.screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))

        # Save to temporary file
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        self.screenshot.save(self.temp_file.name)
        self.temp_file_name = self.temp_file.name
        self.temp_file.close()

        # Display the screenshot
        self.display_screenshot()

    def start_drag(self, event):
        print_event_info(event) # TODO: remove this when done debugging
        # use a tuple as file list, this should hopefully be handled gracefully
        # by tkdnd and the drop targets like file managers or text editors
        data = ()
        #if self.curselection():
        #    data = tuple([self.get(i) for i in self.curselection()])
        data = (self.temp_file_name,)
        print('Dragging :', data)
        # tuples can also be used to specify possible alternatives for
        # action type and DnD type:
        return ((ASK, COPY), (DND_FILES, DND_TEXT), data)

    def end_drag(self, event):
        #print_event_info(event)
        # this callback is not really necessary if it doesn't do anything useful
        self.image_window.deiconify()
        self.root.deiconify()
        print('Drag ended for widget:', event.widget)

    def display_screenshot(self):
        # Create a new window to display the screenshot
        self.image_window = tk.Toplevel(self.root)
        #self.image_window =TkinterDnD.Tk()
        self.image_window.title("Screenshot")
        self.image_window.attributes('-topmost', True)

        # Convert PIL image to Tkinter PhotoImage
        self.tk_image = ImageTk.PhotoImage(self.screenshot)

        # Create a label to display the image
        self.image_label = tk.Label(self.image_window, image=self.tk_image)
        self.image_label.pack()

        # Make the image draggable
        #self.image_label.bind("<ButtonPress-1>", self.start_drag)
        #self.image_label.bind("<B1-Motion>", self.on_image_drag)
        self.image_label.drag_source_register(1, DND_TEXT, DND_FILES)
        self.image_label.dnd_bind('<<DragInitCmd>>', self.start_drag)
        self.image_label.dnd_bind('<<DragEndCmd>>', self.end_drag)

        # Add buttons
        button_frame = tk.Frame(self.image_window)
        button_frame.pack(fill=tk.X, pady=5)

        save_btn = tk.Button(button_frame, text="Save", command=self.save_screenshot)
        save_btn.pack(side=tk.LEFT, padx=5)

        copy_btn = tk.Button(button_frame, text="Copy to Clipboard", command=self.copy_to_clipboard)
        copy_btn.pack(side=tk.LEFT, padx=5)

        delay_btn = tk.Button(button_frame, text="Delay (5s)", command=lambda: self.start_capture(delayed=True))
        delay_btn.pack(side=tk.LEFT, padx=5)

        retry_btn = tk.Button(button_frame, text="Retry", command=self.retry_screenshot)
        retry_btn.pack(side=tk.LEFT, padx=5)

        close_btn = tk.Button(button_frame, text="Close", command=self.image_window.destroy)
        close_btn.pack(side=tk.RIGHT, padx=5)

    def start_drag(self, event):
        # Store initial position for drag operation    print_event_info(event)
        # use a tuple as file list, this should hopefully be handled gracefully
        # by tkdnd and the drop targets like file managers or text editors
        data = ()
        self.image_window.withdraw()
        self.root.withdraw()
        #if self.curselection():
        #    data = tuple([self.get(i) for i in self.curselection()])
        data = (self.temp_file_name,)
        print('Dragging :', data)
        # tuples can also be used to specify possible alternatives for
        # action type and DnD type:
        return ((ASK, COPY), (DND_FILES, DND_TEXT), data)

    def on_image_drag(self, event):
        # Start file drag and drop
        if abs(event.x - self.drag_data['x']) > 10 or abs(event.y - self.drag_data['y']) > 10:
            self.image_label.config(cursor="plus")
            # Start system drag and drop (platform specific)
            if sys.platform == 'win32':
                # For Windows
                import win32clipboard
                from io import BytesIO

                # Put image on clipboard
                output = BytesIO()
                self.screenshot.convert('RGB').save(output, 'BMP')
                data = output.getvalue()[14:]  # The file header offset of BMP is 14 bytes
                output.close()

                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
                win32clipboard.CloseClipboard()

                # Simulate key press to paste
                import win32com.client
                shell = win32com.client.Dispatch("WScript.Shell")
                shell.SendKeys('^v')
            else:
                # For macOS/Linux, use the temp file
                # This is a simplified approach - actual implementation would need
                # to use platform-specific APIs for proper drag and drop
                os.system(f"open {self.temp_file.name}")

    def save_screenshot(self):
        # Ask for filename
        file_path = tk.filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )

        if file_path:
            self.screenshot.save(file_path)
            messagebox.showinfo("Saved", f"Screenshot saved to {file_path}")

    def copy_to_clipboard(self):
        # Copy to clipboard (platform specific)
        if sys.platform == 'win32':
            # For Windows
            import win32clipboard
            from io import BytesIO

            output = BytesIO()
            self.screenshot.convert('RGB').save(output, 'BMP')
            data = output.getvalue()[14:]
            output.close()

            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
            win32clipboard.CloseClipboard()
        else:
            # For Linux/macOS
            # This would need to be implemented with platform-specific code
            messagebox.showinfo("Info", "Clipboard functionality not implemented for this platform")

    def retry_screenshot(self):
        # Close the current screenshot window
        self.image_window.destroy()
        # Start a new capture process
        self.start_capture()

def main():
    root = TkinterDnD.Tk()
    app = ScreenshotApp(root)
    root.mainloop()

    # Clean up temp file
    if app.temp_file and os.path.exists(app.temp_file.name):
        try:
            #os.unlink(app.temp_file.name)
            pass
        except:
            pass



if __name__ == "__main__":
    main()
