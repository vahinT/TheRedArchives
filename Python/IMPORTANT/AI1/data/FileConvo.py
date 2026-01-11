import os
import shutil
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox, scrolledtext

# Ensure tkinterdnd2 is installed
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "tkinterdnd2"])
    from tkinterdnd2 import DND_FILES, TkinterDnD  # Retry import

# Function to handle dropped files
def handle_drop(event):
    dropped_files = root.tk.splitlist(event.data)
    if not dropped_files:
        return
    files.clear()
    for f in dropped_files:
        if os.path.isfile(f):
            files.append(f)
    log_output.insert(tk.END, f"{len(files)} file(s) ready for conversion.\n")

# File conversion logic
def convert_files():
    new_ext = ext_entry.get().strip()

    if not files:
        messagebox.showwarning("No Files", "Please drag and drop files first.")
        return

    if not new_ext:
        messagebox.showerror("Invalid Extension", "Extension cannot be empty.")
        return

    if not new_ext.startswith('.'):
        new_ext = '.' + new_ext

    log_output.delete("1.0", tk.END)

    for file_path in files:
        dir_name = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)
        root_name = os.path.splitext(file_name)[0]
        new_name = f"{root_name}{new_ext}"
        new_path = os.path.join(dir_name, new_name)

        counter = 1
        while os.path.exists(new_path):
            new_name = f"{root_name}_{counter}{new_ext}"
            new_path = os.path.join(dir_name, new_name)
            counter += 1

        try:
            shutil.copy2(file_path, new_path)
            log_output.insert(tk.END, f"Created: {os.path.basename(new_path)}\n")
        except Exception as e:
            log_output.insert(tk.END, f"Failed to create {new_name}: {str(e)}\n")

# GUI Setup
root = TkinterDnD.Tk()
root.title("FileConvo")
root.geometry("500x450")

files = []

frame = tk.Frame(root, padx=10, pady=10)
frame.pack(fill="both", expand=True)

tk.Label(frame, text="New File Extension (e.g., .txt, .png):").pack(anchor="w")
ext_entry = tk.Entry(frame)
ext_entry.pack(fill="x")

tk.Button(frame, text="Convert Files", command=convert_files).pack(pady=10)

drop_area = tk.Label(frame, text="Drag and Drop Files Here", relief="groove", height=4, bg="#f0f0f0")
drop_area.pack(fill="both", expand=True, pady=5)
drop_area.drop_target_register(DND_FILES)
drop_area.dnd_bind("<<Drop>>", handle_drop)

log_output = scrolledtext.ScrolledText(frame, height=10)
log_output.pack(fill="both", expand=True)

root.mainloop()
