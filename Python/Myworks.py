import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import time
import sys

def update_progress(progressbar, root):
    for i in range(101):
        progressbar['value'] = i
        root.update()
        time.sleep(0.05)  

def main():
    input1 = messagebox.askyesno("Question", "Do you want to proceed?")

    if input1:
        root = tk.Tk()
        root.title("Progress")
        progressbar = ttk.Progressbar(root, orient='horizontal', mode='determinate', length=200, maximum=100)
        progressbar.pack(pady=20)

        update_progress(progressbar, root)
        root.mainloop()
    else:
        input2 = messagebox.askyesno("Question", "Do you want to Quit?")
        if input2:
            messagebox.showwarning("Warning!", "Aborting....")
            sys.exit()
        else:
            
            root = tk.Tk()
            root.withdraw()  
            main()

main()
