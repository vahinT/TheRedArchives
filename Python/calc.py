import tkinter as tk

class Calculator:
    def __init__(self, master):
        self.master = master
        master.title("Simple Calculator")

        self.expression = ""
        self.input_text = tk.StringVar()

        # Input field
        self.input_frame = tk.Frame(master, bd=2, relief=tk.RAISED)
        self.input_frame.pack(side=tk.TOP)

        self.input_field = tk.Entry(self.input_frame, font=('arial', 18, 'bold'),
                                     textvariable=self.input_text, width=28, bg="#eee", bd=0,
                                     justify=tk.RIGHT)
        self.input_field.grid(row=0, column=0, columnspan=4, ipadx=8, ipady=8)

        # Buttons
        self.btns_frame = tk.Frame(master, bd=0, relief=tk.RAISED)
        self.btns_frame.pack()

        # Row 1
        self.create_button("7", 1, 0)
        self.create_button("8", 1, 1)
        self.create_button("9", 1, 2)
        self.create_button("/", 1, 3, fg="orange")

        # Row 2
        self.create_button("4", 2, 0)
        self.create_button("5", 2, 1)
        self.create_button("6", 2, 2)
        self.create_button("*", 2, 3, fg="orange")

        # Row 3
        self.create_button("1", 3, 0)
        self.create_button("2", 3, 1)
        self.create_button("3", 3, 2)
        self.create_button("-", 3, 3, fg="orange")

        # Row 4
        self.create_button("C", 4, 0, bg="#ff6666")
        self.create_button("0", 4, 1)
        self.create_button("=", 4, 2, bg="#66ff66")
        self.create_button("+", 4, 3, fg="orange")

        # Row 5 (for decimal)
        self.create_button(".", 5, 0)


    def create_button(self, text, row, column, columnspan=1, bg="#fff", fg="black"):
        button = tk.Button(self.btns_frame, text=text, fg=fg, width=7, height=3, bd=0, bg=bg,
                           cursor="hand2", command=lambda: self.button_click(text),
                           font=('arial', 14, 'bold'))
        button.grid(row=row, column=column, columnspan=columnspan, padx=1, pady=1)

    def button_click(self, item):
        if item == "C":
            self.expression = ""
            self.input_text.set("")
        elif item == "=":
            try:
                result = str(eval(self.expression))
                self.input_text.set(result)
                self.expression = result
            except:
                self.input_text.set("Error")
                self.expression = ""
        else:
            self.expression += str(item)
            self.input_text.set(self.expression)

if __name__ == "__main__":
    root = tk.Tk()
    my_calculator = Calculator(root)
    root.mainloop()