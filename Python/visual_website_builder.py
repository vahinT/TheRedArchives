import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import html
import re

class VisualWebsiteBuilder(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Visual Website Builder")
        self.geometry("900x600")

        self.elements = []  # List of elements added to the canvas

        self.create_widgets()

    def create_widgets(self):
        # Left frame: toolbox
        toolbox_frame = ttk.Frame(self, width=150)
        toolbox_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        ttk.Label(toolbox_frame, text="Toolbox").pack(pady=5)

        # Toolbox buttons
        ttk.Button(toolbox_frame, text="Add Button", command=self.add_button).pack(fill=tk.X, pady=2)
        ttk.Button(toolbox_frame, text="Add Image", command=self.add_image).pack(fill=tk.X, pady=2)
        ttk.Button(toolbox_frame, text="Add Text", command=self.add_text).pack(fill=tk.X, pady=2)

        # Center frame: visual canvas
        canvas_frame = ttk.Frame(self)
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        ttk.Label(canvas_frame, text="Visual Layout").pack()

        self.canvas = tk.Canvas(canvas_frame, bg="white", relief=tk.SUNKEN, borderwidth=1)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Right frame: code editor
        code_frame = ttk.Frame(self, width=300)
        code_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        ttk.Label(code_frame, text="Generated HTML Code").pack(pady=5)

        self.code_editor = scrolledtext.ScrolledText(code_frame, wrap=tk.WORD, width=40)
        self.code_editor.pack(fill=tk.BOTH, expand=True)

        # Buttons for code editor
        btn_frame = ttk.Frame(code_frame)
        btn_frame.pack(fill=tk.X, pady=5)

        ttk.Button(btn_frame, text="Copy Code", command=self.copy_code).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Refresh Visual", command=self.refresh_visual_from_code).pack(side=tk.LEFT, padx=5)

    def add_button(self):
        # Add a button element to the canvas
        btn = tk.Button(self.canvas, text="Button")
        btn_id = self.canvas.create_window(50, 50 + 30 * len(self.elements), window=btn, anchor="nw")
        self.elements.append(("button", btn, btn_id))
        self.update_code()

    def add_image(self):
        # Add an image element placeholder to the canvas
        # For simplicity, just add a label with [Image src]
        lbl = tk.Label(self.canvas, text="[Image src]", bg="lightgray")
        lbl_id = self.canvas.create_window(50, 50 + 30 * len(self.elements), window=lbl, anchor="nw")
        self.elements.append(("image", lbl, lbl_id))
        self.update_code()

    def add_text(self):
        # Add a text element to the canvas
        lbl = tk.Label(self.canvas, text="Sample Text")
        lbl_id = self.canvas.create_window(50, 50 + 30 * len(self.elements), window=lbl, anchor="nw")
        self.elements.append(("text", lbl, lbl_id))
        self.update_code()

    def update_code(self):
        # Generate HTML code from elements
        html_lines = ["<html>", "<body>"]
        for elem_type, widget, _ in self.elements:
            if elem_type == "button":
                text = widget.cget("text")
                html_lines.append(f'  <button>{html.escape(text)}</button>')
            elif elem_type == "image":
                # Placeholder src attribute
                html_lines.append('  <img src="path/to/image.jpg" alt="Image"/>')
            elif elem_type == "text":
                text = widget.cget("text")
                html_lines.append(f'  <p>{html.escape(text)}</p>')
        html_lines.append("</body>")
        html_lines.append("</html>")

        code = "\n".join(html_lines)
        self.code_editor.delete(1.0, tk.END)
        self.code_editor.insert(tk.END, code)

    def copy_code(self):
        code = self.code_editor.get(1.0, tk.END)
        try:
            import pyperclip
            pyperclip.copy(code)
            messagebox.showinfo("Copied", "Code copied to clipboard!")
        except ImportError:
            messagebox.showerror("Error", "pyperclip module not installed. Cannot copy to clipboard.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy code: {e}")

    def refresh_visual_from_code(self):
        # Parse the HTML code and update the visual canvas accordingly
        code = self.code_editor.get(1.0, tk.END)
        # Clear current elements from canvas
        for _, widget, widget_id in self.elements:
            self.canvas.delete(widget_id)
            widget.destroy()
        self.elements.clear()

        # Simple regex-based parsing for <button>, <img>, <p> tags
        button_pattern = re.compile(r'<button>(.*?)</button>', re.IGNORECASE | re.DOTALL)
        img_pattern = re.compile(r'<img\s+[^>]*src=["\']([^"\']*)["\'][^>]*>', re.IGNORECASE)
        p_pattern = re.compile(r'<p>(.*?)</p>', re.IGNORECASE | re.DOTALL)

        y_pos = 50
        line_height = 30

        # Find all buttons
        for match in button_pattern.finditer(code):
            text = html.unescape(match.group(1).strip())
            btn = tk.Button(self.canvas, text=text)
            btn_id = self.canvas.create_window(50, y_pos, window=btn, anchor="nw")
            self.elements.append(("button", btn, btn_id))
            y_pos += line_height

        # Find all images
        for match in img_pattern.finditer(code):
            src = match.group(1).strip()
            # For simplicity, show label with src text
            lbl = tk.Label(self.canvas, text=f"[Image: {src}]", bg="lightgray")
            lbl_id = self.canvas.create_window(50, y_pos, window=lbl, anchor="nw")
            self.elements.append(("image", lbl, lbl_id))
            y_pos += line_height

        # Find all paragraphs
        for match in p_pattern.finditer(code):
            text = html.unescape(match.group(1).strip())
            lbl = tk.Label(self.canvas, text=text)
            lbl_id = self.canvas.create_window(50, y_pos, window=lbl, anchor="nw")
            self.elements.append(("text", lbl, lbl_id))
            y_pos += line_height

        if not self.elements:
            messagebox.showinfo("Info", "No recognizable elements found in code.")

if __name__ == "__main__":
    app = VisualWebsiteBuilder()
    app.mainloop()
