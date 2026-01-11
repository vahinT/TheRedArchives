import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os, subprocess, tempfile, re, platform, pathlib
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageTk

# ------------------ THEME DETECTION ------------------
def detect_system_theme():
    try:
        if platform.system() == "Windows":
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize") as key:
                return "light" if winreg.QueryValueEx(key,"AppsUseLightTheme")[0]==1 else "dark"
    except: pass
    return "dark"

# ------------------ MAIN IDE ------------------
class VamCodeo:
    def __init__(self, root):
        self.root = root
        self.root.title("VamCodeo")
        self.root.minsize(600,400)
        self._base_title="VamCodeo"
        self.theme = detect_system_theme()

        self.keywords=[ "and","as","assert","async","await","break","class","continue","def","del",
                        "elif","else","except","False","finally","for","from","global","if","import",
                        "in","is","lambda","None","nonlocal","not","or","pass","raise","return",
                        "True","try","while","with","yield" ]
        self.builtins=["print","len","str","int","float","bool","list","tuple","dict","set","range","open","input","exit"]

        self.tabs={}
        self.sidebar=tk.PanedWindow(self.root,orient=tk.HORIZONTAL)
        self.sidebar.pack(fill=tk.BOTH,expand=True)

        # FILE TREE
        self.file_tree_frame=tk.Frame(self.sidebar,width=200)
        self.file_tree=ttk.Treeview(self.file_tree_frame)
        self.file_tree.pack(fill=tk.BOTH,expand=True,side=tk.LEFT)
        ttk.Scrollbar(self.file_tree_frame,command=self.file_tree.yview).pack(fill=tk.Y,side=tk.RIGHT)
        self.sidebar.add(self.file_tree_frame)
        self._populate_file_tree(pathlib.Path.cwd())
        self.file_tree.bind("<Double-1>",self._on_file_tree_open)

        # TABS
        self.tab_control=ttk.Notebook(self.sidebar)
        self.sidebar.add(self.tab_control)
        self.tab_control.bind("<<NotebookTabChanged>>",lambda e:self._update_title())
        self.tab_control.bind("<Button-1>",self._on_tab_click)
        self._create_new_tab()

        # OUTPUT
        self.output_area=tk.Text(self.root,height=10,state=tk.DISABLED)
        self.output_area.pack(fill=tk.BOTH)

        self.apply_theme()

    # ------------------ TAB HANDLING ------------------
    def _create_new_tab(self, content="", title="Untitled", file_path=None):
        tab=tk.Frame(self.tab_control)
        self.tab_control.add(tab,text=f"{title}  ✕")
        self.tab_control.select(tab)

        editor=tk.Text(tab,undo=True,wrap=tk.NONE)
        editor.pack(fill=tk.BOTH,expand=True)
        editor.insert("1.0",content)
        editor.bind("<KeyRelease>",lambda e:self._highlight(editor))
        self.tabs[tab]={"text":editor,"file":file_path}
        self._highlight(editor)
        self._update_title()

    def _on_tab_click(self,event):
        try:
            i=self.tab_control.index(f"@{event.x},{event.y}")
            tab=self.tab_control.tabs()[i]
            if self.tab_control.tab(tab,"text").endswith("✕"):
                self._close_tab(tab)
        except: pass

    def _close_tab(self,tab):
        self.tab_control.forget(tab)
        del self.tabs[self.root.nametowidget(tab)]
        self._update_title()

    # ------------------ FILE TREE ------------------
    def _populate_file_tree(self,path,parent=""):
        try:
            for p in sorted(path.iterdir(),key=lambda x:(not x.is_dir(),x.name.lower())):
                nid=self.file_tree.insert(parent,"end",text=p.name)
                if p.is_dir(): self._populate_file_tree(p,nid)
        except PermissionError: pass

    def _on_file_tree_open(self,event):
        node=self.file_tree.focus()
        names=[]
        while node:
            names.insert(0,self.file_tree.item(node,"text"))
            node=self.file_tree.parent(node)
        full=os.path.join(*names)
        if os.path.isfile(full):
            self._create_new_tab(open(full,encoding="utf-8").read(),os.path.basename(full),full)

    # ------------------ HIGHLIGHT ------------------
    def _highlight(self,widget):
        for tag in ["kw","num","str","com"]:
            widget.tag_remove(tag,"1.0",tk.END)
        code=widget.get("1.0",tk.END)
        for i,l in enumerate(code.splitlines()):
            ln=i+1
            for kw in self.keywords:
                for m in re.finditer(rf"\b{kw}\b",l):
                    widget.tag_add("kw",f"{ln}.{m.start()}",f"{ln}.{m.end()}")
            if (m:=re.search(r"#.*",l)):
                widget.tag_add("com",f"{ln}.{m.start()}",f"{ln}.{m.end()}")
        widget.tag_config("kw",foreground="orange")
        widget.tag_config("com",foreground="grey")

    def _update_title(self):
        self.root.title(self._base_title)

    def apply_theme(self): pass


root=tk.Tk()
VamCodeo(root)
root.mainloop()
