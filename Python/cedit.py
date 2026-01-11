import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageDraw, ImageFont, ImageTk
from io import BytesIO
import os, re, platform, pathlib, subprocess, tempfile


def detect_system_theme():
    try:
        system = platform.system()
        if system == "Windows":
            import winreg
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize"
            ) as key:
                value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                return "light" if value == 1 else "dark"
        elif system == "Darwin":
            result = subprocess.run(
                ["defaults", "read", "-g", "AppleInterfaceStyle"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            return "dark" if "Dark" in result.stdout else "light"
    except Exception as e:
        print("[Theme Detection] Failed:", e)
    return "dark"


def generate_app_icon(root):
    try:
        img_size = 1024
        img = Image.new("RGB", (img_size, img_size), "red")
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", 700)
        except IOError:
            font = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), "<>", font=font)
        x = (img_size - (bbox[2] - bbox[0])) // 2 - bbox[0]
        y = (img_size - (bbox[3] - bbox[1])) // 2 - bbox[1]
        draw.text((x, y), "<>", fill="white", font=font)
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        icon_img = ImageTk.PhotoImage(Image.open(buffer))
        root.iconphoto(True, icon_img)
        return icon_img
    except Exception as e:
        print("[Icon Error]", e)
        return None


class VamCodeo:
    def __init__(self, root):
        self.root = root
        self.root.title("VamCodeo - C++ Editor")
        self.root.minsize(600, 400)
        self._base_title = "VamCodeo - C++ Editor"
        self.icon_img_ref = generate_app_icon(self.root)

        self.theme = detect_system_theme()
        self.themes = {
            "dark": {
                "bg": "#1e1e1e", "fg": "#dcdcdc", "insert": "white",
                "line_bg": "#2d2d2d", "output_bg": "#2e2e2e", "output_fg": "#c5c5c5",
                "keyword": "#569CD6", "comment": "#6A9955", "string": "#CE9178",
                "number": "#B5CEA8", "operator": "#D4D4D4", "builtin": "#4EC9B0"
            },
            "light": {
                "bg": "white", "fg": "black", "insert": "black",
                "line_bg": "#f0f0f0", "output_bg": "#e8e8e8", "output_fg": "black",
                "keyword": "blue", "comment": "green", "string": "brown",
                "number": "purple", "operator": "darkorange", "builtin": "navy"
            }
        }
        self.colors = self.themes.get(self.theme, self.themes["dark"])

        self._setup_widgets()

    def _setup_widgets(self):
        self.text = tk.Text(
            self.root, wrap="none", undo=True,
            bg=self.colors["bg"], fg=self.colors["fg"], insertbackground=self.colors["insert"]
        )
        self.text.pack(fill="both", expand=True)

        self._add_menu()

    def _add_menu(self):
        menu_bar = tk.Menu(self.root)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Open", command=self._open_file)
        file_menu.add_command(label="Save", command=self._save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)
        self.root.config(menu=menu_bar)

    def _open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("C++ Files", "*.cpp;*.h"), ("All Files", "*.*")])
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.text.delete("1.0", tk.END)
                self.text.insert(tk.END, content)
                self.root.title(f"{self._base_title} - {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file:\n{e}")

    def _save_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".cpp",
                                                 filetypes=[("C++ Files", "*.cpp;*.h"), ("All Files", "*.*")])
        if file_path:
            try:
                content = self.text.get("1.0", tk.END)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                self.root.title(f"{self._base_title} - {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file:\n{e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = VamCodeo(root)
    root.mainloop()
