import subprocess
import sys
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

# Auto-install requests
try:
    import requests
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "requests"])
    import requests

# Predefined list of common packages
common_packages = [
    "requests", "numpy", "pandas", "flask", "django", "matplotlib",
    "scipy", "pygame", "selenium", "opencv-python", "beautifulsoup4",
    "tkinter", "pyinstaller", "scikit-learn", "openpyxl", "torch"
]

# Function to check if the package exists on PyPI using JSON API
def check_package_exists(package):
    try:
        response = requests.get(f"https://pypi.org/pypi/{package}/json", timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

# Function to install the package
def install_package():
    package = package_combobox.get().strip()
    if not package:
        messagebox.showwarning("Missing Input", "Please enter or select a package.")
        return

    install_button.config(state=tk.DISABLED)
    output_text.insert(tk.END, f"> Installing '{package}'...\n")
    output_text.see(tk.END)

    def run_install():
        if not check_package_exists(package):
            output_text.insert(tk.END, f"⚠️ Package not found on PyPI. Trying install anyway...\n")

        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", package],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            output_text.insert(tk.END, result.stdout + "\n")
        except Exception as e:
            output_text.insert(tk.END, f"❌ Error: {e}\n")
        finally:
            install_button.config(state=tk.NORMAL)
            output_text.see(tk.END)

    threading.Thread(target=run_install).start()

# GUI setup
root = tk.Tk()
root.title("Python Package Installer")
root.geometry("700x450")

tk.Label(root, text="Select or type a Python package:", font=("Arial", 12)).pack(pady=5)

package_combobox = ttk.Combobox(root, values=common_packages, width=50, font=("Arial", 12))
package_combobox.pack(pady=5)
package_combobox.set("")  # Start empty

install_button = tk.Button(root, text="Install Package", command=install_package,
                           bg="#4CAF50", fg="white", font=("Arial", 12))
install_button.pack(pady=10)

output_text = scrolledtext.ScrolledText(root, width=80, height=15, font=("Courier", 10))
output_text.pack(pady=10)

root.mainloop()
