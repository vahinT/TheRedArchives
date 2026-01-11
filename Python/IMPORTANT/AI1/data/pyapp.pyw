import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import os

class CollapsibleSection(tk.Frame):
    def __init__(self, parent, title="Section", *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.toggle = tk.IntVar(value=0)
        self.header = ttk.Checkbutton(self, text=title, variable=self.toggle, command=self.toggle_section, style="Toolbutton")
        self.header.pack(fill="x")
        self.content = tk.Frame(self)
        self.content.pack(fill="x", expand=True)
        self.content.forget()

    def toggle_section(self):
        if self.toggle.get():
            self.content.pack(fill="x", expand=True)
        else:
            self.content.forget()

class AppMaker(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Pyapp v1.4.5")
        self.geometry("1920x1080")
        self.option_vars = {}
        self.radio_vars = {}
        self.create_main_layout()

    def create_main_layout(self):
        container = tk.Frame(self)
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.build_sections(scrollable_frame)

        file_frame = tk.LabelFrame(self, text="📄 Select Python File to Package", padx=5, pady=5)
        file_frame.pack(fill="x", padx=10, pady=5)
        self.py_path_var = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.py_path_var)
        file_entry.pack(side="left", fill="x", expand=True, padx=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_py_file).pack(side="right", padx=5)

        build_btn = ttk.Button(self, text="🚀 Build App", command=self.build_command)
        build_btn.pack(pady=5)

        out_frame = tk.LabelFrame(self, text="🖨️ Output", padx=5, pady=5)
        out_frame.pack(fill="both", expand=True, padx=10, pady=5)
        self.output = scrolledtext.ScrolledText(out_frame, height=10, state="disabled")
        self.output.pack(fill="both", expand=True)

    def build_sections(self, parent):
        self.sections = {
            "basic":     CollapsibleSection(parent, "🛠️ Basic Build Options"),
            "console":   CollapsibleSection(parent, "🖥️ Console / Windowed Mode"),
            "upx":       CollapsibleSection(parent, "📦 Compression / UPX"),
            "files":     CollapsibleSection(parent, "📁 Include Files"),
            "imports":   CollapsibleSection(parent, "🧩 Import Handling"),
            "env":       CollapsibleSection(parent, "🐍 Environment / Cleanup"),
            "debug":     CollapsibleSection(parent, "🧪 Debugging / Logging"),
            "spec":      CollapsibleSection(parent, "🔧 Spec File"),
        }

        for section in self.sections.values():
            section.pack(fill="x", padx=10, pady=5)

        self.add_checkboxes(self.sections["basic"].content, [
            ("--onefile", "Bundle into one file"),
            ("--onedir", "Bundle into one folder"),
            ("--noconfirm", "Replace output directory without asking"),
        ])
        self.add_entry(self.sections["basic"].content, "--name")
        self.add_entry(self.sections["basic"].content, "--specpath")
        self.add_entry(self.sections["basic"].content, "--distpath")
        self.add_entry(self.sections["basic"].content, "--workpath")
        self.add_icon_entry(self.sections["basic"].content, "--icon")  # Icon selection

        self.add_radio(self.sections["console"].content, "Console Mode", [
            ("--console", "Console"),
            ("--windowed", "Windowed")
        ])
        self.add_radio(self.sections["console"].content, "Window Mode", [
            ("--noconsole", "No Console"),
            ("--nowindowed", "No Window")
        ])

        self.add_entry(self.sections["upx"].content, "--upx-dir")
        self.add_checkboxes(self.sections["upx"].content, [("--noupx", "Disable UPX compression")])

        self.add_file_list(self.sections["files"].content, "--add-data")
        self.add_file_list(self.sections["files"].content, "--add-binary")

        self.add_entry(self.sections["imports"].content, "--hidden-import")
        self.add_entry(self.sections["imports"].content, "--exclude-module")

        self.add_checkboxes(self.sections["env"].content, [("--clean", "Clean PyInstaller cache")])
        self.add_entry(self.sections["env"].content, "--runtime-tmpdir")

        self.add_checkboxes(self.sections["debug"].content, [("--debug all", "Enable all debugging")])
        self.add_entry(self.sections["debug"].content, "--log-level")

        self.add_entry(self.sections["spec"].content, "SPEC FILE")

    def add_checkboxes(self, parent, options):
        for flag, text in options:
            var = tk.BooleanVar()
            self.option_vars[flag] = var
            cb = ttk.Checkbutton(parent, text=text, variable=var)
            cb.pack(anchor="w", padx=10, pady=2)

    def add_entry(self, parent, flag):
        frame = tk.Frame(parent)
        frame.pack(fill="x", padx=10, pady=2)
        tk.Label(frame, text=flag).pack(side="left")
        entry = ttk.Entry(frame)
        entry.pack(side="right", fill="x", expand=True)
        self.option_vars[flag] = entry

    def add_icon_entry(self, parent, flag):
        frame = tk.Frame(parent)
        frame.pack(fill="x", padx=10, pady=2)
        tk.Label(frame, text=flag).pack(side="left")

        icon_var = tk.StringVar()
        entry = ttk.Entry(frame, textvariable=icon_var)
        entry.pack(side="left", fill="x", expand=True, padx=5)
        self.option_vars[flag] = entry

        def browse_icon():
            path = filedialog.askopenfilename(filetypes=[("Icon Files", "*.ico")])
            if path:
                icon_var.set(path)

        ttk.Button(frame, text="Browse", command=browse_icon).pack(side="right")

    def add_file_list(self, parent, flag):
        frame = tk.Frame(parent)
        frame.pack(fill="x", padx=10, pady=2)
        listbox = tk.Listbox(frame, height=3)
        listbox.pack(side="left", fill="x", expand=True, padx=5)
        self.option_vars[flag] = listbox

        def add_item():
            path = filedialog.askopenfilename()
            if path:
                dest = os.path.basename(path)
                pair = f"{path};{dest}"
                listbox.insert(tk.END, pair)

        def remove_selected():
            selected = listbox.curselection()
            for i in reversed(selected):
                listbox.delete(i)

        btn_frame = tk.Frame(frame)
        btn_frame.pack(side="right")
        ttk.Button(btn_frame, text="Add", command=add_item).pack(fill="x")
        ttk.Button(btn_frame, text="Remove", command=remove_selected).pack(fill="x")

    def add_radio(self, parent, label, options):
        frame = tk.LabelFrame(parent, text=label)
        frame.pack(fill="x", padx=10, pady=2)
        var = tk.StringVar()
        self.radio_vars[label] = var
        for val, txt in options:
            ttk.Radiobutton(frame, text=txt, variable=var, value=val).pack(anchor="w")

    def browse_py_file(self):
        path = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
        if path:
            self.py_path_var.set(path)

    def append_output(self, text):
        self.output.configure(state="normal")
        self.output.insert(tk.END, text + "\n")
        self.output.see(tk.END)
        self.output.configure(state="disabled")

    def build_command(self):
        cmd = ["pyinstaller"]

        pyfile = self.py_path_var.get().strip()
        if pyfile:
            cmd.append(pyfile)

        for flag, widget in self.option_vars.items():
            if isinstance(widget, tk.BooleanVar) and widget.get():
                cmd.append(flag)
            elif isinstance(widget, ttk.Entry):
                value = widget.get().strip()
                if value:
                    if flag == "SPEC FILE":
                        cmd.append(value)
                    else:
                        cmd.append(flag)
                        cmd.append(value)
            elif isinstance(widget, tk.Listbox):
                for i in widget.get(0, tk.END):
                    if ";" in i:
                        cmd.append(flag)
                        cmd.append(i)

        for label, var in self.radio_vars.items():
            if var.get():
                cmd.append(var.get())

        self.append_output("Running: " + " ".join(cmd))
        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in proc.stdout:
                self.append_output(line.strip())
        except Exception as e:
            self.append_output(f"Error: {e}")

if __name__ == "__main__":
    AppMaker().mainloop()
