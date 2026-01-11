# client.py
import subprocess, sys , os
def ensure_module(pkg, imp=None):
    try:
        __import__(imp or pkg)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

ensure_module("requests")
ensure_module("Pillow", "PIL")

import tkinter as tk
from tkinter import ttk, filedialog, simpledialog, messagebox
from PIL import Image, ImageTk
import requests, threading, time, io, webbrowser

SERVER_URL = 'http://localhost:5000'

def login_flow():
    # hidden root for dialogs
    root = tk.Tk()
    root.withdraw()
    username = None
    while username is None:
        have_acc = messagebox.askyesno("Hiver", "Do you have an account?")
        if have_acc:
            u = simpledialog.askstring("Login", "Username:", parent=root)
            p = simpledialog.askstring("Login", "Password:", show='*', parent=root)
            if not u or not p:
                messagebox.showerror("Error", "Username and password required.", parent=root)
                continue
            resp = requests.post(f"{SERVER_URL}/login", json={'username': u, 'password': p})
            if resp.status_code == 200:
                username = u
            else:
                messagebox.showerror("Error", resp.json().get('error','Login failed'), parent=root)
        else:
            u = simpledialog.askstring("Register", "Choose username:", parent=root)
            p = simpledialog.askstring("Register", "Choose password:", show='*', parent=root)
            if not u or not p:
                messagebox.showerror("Error", "Username and password required.", parent=root)
                continue
            resp = requests.post(f"{SERVER_URL}/register", json={'username': u, 'password': p})
            if resp.status_code == 201:
                messagebox.showinfo("Hiver", "Registered! You can now log in.", parent=root)
            else:
                messagebox.showerror("Error", resp.json().get('error','Registration failed'), parent=root)
    root.destroy()
    return username

class HiverApp(tk.Tk):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.title(f'Hiver — {self.username}')
        self.geometry('700x500')
        self.current_chat = None
        self.image_cache = []
        self.create_widgets()
        self.refresh_chats()
        self.auto_refresh()

    def create_widgets(self):
        frame = ttk.Frame(self); frame.pack(fill=tk.BOTH, expand=True)
        self.listbox = tk.Listbox(frame); self.listbox.pack(side=tk.LEFT, fill=tk.Y)
        self.listbox.bind('<<ListboxSelect>>', self.on_select)

        ctrl = ttk.Frame(frame); ctrl.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ttk.Button(ctrl, text='New Chat',    command=self.new_chat).pack(pady=2)
        ttk.Button(ctrl, text='Delete Chat', command=self.delete_chat).pack(pady=2)

        # scrollable canvas for messages
        self.chat_canvas = tk.Canvas(ctrl)
        self.chat_scroll = ttk.Scrollbar(ctrl, orient='vertical', command=self.chat_canvas.yview)
        self.chat_canvas.configure(yscrollcommand=self.chat_scroll.set)
        self.chat_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.chat_canvas.pack(fill=tk.BOTH, expand=True)
        self.chat_window = tk.Frame(self.chat_canvas)
        self.chat_canvas.create_window((0,0), window=self.chat_window, anchor='nw')
        self.chat_window.bind('<Configure>',
            lambda e: self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all")))

        entry = ttk.Frame(ctrl); entry.pack(fill=tk.X, pady=2)
        self.msg_entry = ttk.Entry(entry); self.msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(entry, text='Send',   command=self.send_message).pack(side=tk.LEFT, padx=2)
        ttk.Button(entry, text='Attach', command=self.attach_file).pack(side=tk.LEFT)

    def refresh_chats(self):
        try:
            r = requests.get(f"{SERVER_URL}/chats")
            if r.status_code == 200:
                self.listbox.delete(0, tk.END)
                for chat in r.json().get('chats', []):
                    self.listbox.insert(tk.END, chat)
        except: pass

    def new_chat(self):
        cid = simpledialog.askstring('New Chat', 'Chat ID:')
        if cid:
            r = requests.post(f"{SERVER_URL}/create_chat", json={'chat_id': cid})
            if r.status_code == 201:
                self.refresh_chats()

    def delete_chat(self):
        sel = self.listbox.curselection()
        if not sel: return
        cid = self.listbox.get(sel)
        r = requests.post(f"{SERVER_URL}/delete_chat", json={'chat_id': cid})
        if r.status_code == 200:
            self.current_chat = None
            # clear messages
            for w in self.chat_window.winfo_children():
                w.destroy()
            self.refresh_chats()

    def on_select(self, _):
        sel = self.listbox.curselection()
        if sel:
            self.current_chat = self.listbox.get(sel)
            self.load_messages()

    def auto_refresh(self):
        def loop():
            while True:
                if self.current_chat:
                    self.load_messages()
                time.sleep(0.5)
        threading.Thread(target=loop, daemon=True).start()

    def load_messages(self):
        try:
            r = requests.get(f"{SERVER_URL}/get_messages", params={'chat_id': self.current_chat})
            if r.status_code != 200: return
            msgs = r.json().get('messages', [])
            # rebuild
            for w in self.chat_window.winfo_children():
                w.destroy()
            self.image_cache.clear()

            for msg in msgs:
                lbl = ttk.Label(self.chat_window,
                    text=f"[{msg['timestamp']}] {msg['sender']}: {msg['text']}",
                    wraplength=500, justify='left')
                lbl.pack(anchor='w', padx=5, pady=2)

                if msg.get('media'):
                    url = SERVER_URL + msg['media']['url']
                    ext = url.lower().rsplit('.', 1)[-1]
                    if ext in ('png','jpg','jpeg','gif'):
                        try:
                            img_data = requests.get(url).content
                            img = Image.open(io.BytesIO(img_data))
                            img.thumbnail((200,200))
                            tkimg = ImageTk.PhotoImage(img)
                            self.image_cache.append(tkimg)
                            tk.Label(self.chat_window, image=tkimg).pack(anchor='w', padx=10)
                        except: pass
                    elif ext in ('mp4','webm','mov'):
                        ln = ttk.Label(self.chat_window, text=f"[Video] {os.path.basename(url)}",
                                        foreground="blue", cursor="hand2")
                        ln.pack(anchor='w', padx=10)
                        ln.bind("<Button-1>", lambda e, u=url: webbrowser.open(u))
                    elif ext in ('mp3','wav','ogg'):
                        ln = ttk.Label(self.chat_window, text=f"[Audio] {os.path.basename(url)}",
                                        foreground="blue", cursor="hand2")
                        ln.pack(anchor='w', padx=10)
                        ln.bind("<Button-1>", lambda e, u=url: webbrowser.open(u))
        except:
            pass

    def send_message(self):
        txt = self.msg_entry.get().strip()
        if txt and self.current_chat:
            requests.post(f"{SERVER_URL}/send_message",
                          data={'chat_id': self.current_chat, 'sender': self.username, 'text': txt})
            self.msg_entry.delete(0, tk.END)

    def attach_file(self):
        if not self.current_chat: return
        path = filedialog.askopenfilename()
        if not path: return
        with open(path, 'rb') as f:
            requests.post(f"{SERVER_URL}/send_message",
                          data={'chat_id': self.current_chat, 'sender': self.username},
                          files={'file': f})

if __name__ == '__main__':
    user = login_flow()
    app = HiverApp(user)
    app.mainloop()
