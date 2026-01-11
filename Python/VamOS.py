import tkinter as tk
from tkinter import Toplevel
from PIL import Image, ImageTk
import base64
import io
import os

# Embedded wallpaper base64 (shortened for readability – use full version in actual code)
wallpaper_base64 = """
/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAx
... (insert the full base64 string here without cutting it) ...
"""

class VamOS:
    def __init__(self, root):
        self.root = root
        self.root.title("VamOS")
        self.root.attributes('-fullscreen', True)
        self.set_wallpaper()
        self.create_shutdown_button()
        self.create_start_menu()

    def set_wallpaper(self):
        image_data = base64.b64decode(wallpaper_base64)
        image = Image.open(io.BytesIO(image_data))
        self.wallpaper = ImageTk.PhotoImage(image)

        self.canvas = tk.Canvas(self.root, width=image.width, height=image.height)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, image=self.wallpaper, anchor="nw")

    def create_shutdown_button(self):
        shutdown_btn = tk.Button(self.root, text="Shutdown", font=("Segoe UI", 12), command=self.shutdown)
        self.canvas.create_window(50, 50, window=shutdown_btn)

    def create_start_menu(self):
        self.start_menu = Toplevel(self.root)
        self.start_menu.withdraw()
        self.start_menu.overrideredirect(True)
        self.start_menu.geometry("200x300+10+800")
        self.start_menu.configure(bg="#222")

        tk.Label(self.start_menu, text="Start Menu", fg="white", bg="#222", font=("Segoe UI", 14)).pack(pady=10)

        start_btn = tk.Button(self.root, text="Start", font=("Segoe UI", 12), command=self.toggle_start_menu)
        self.canvas.create_window(100, 50, window=start_btn)

    def toggle_start_menu(self):
        if self.start_menu.winfo_ismapped():
            self.start_menu.withdraw()
        else:
            self.start_menu.deiconify()

    def shutdown(self):
        os._exit(0)

if __name__ == "__main__":
    root = tk.Tk()
    app = VamOS(root)
    root.mainloop()

