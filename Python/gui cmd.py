import tkinter as tk
from tkinter import ttk, scrolledtext
import subprocess
import platform

# Define CMD and PowerShell commands with descriptions
COMMANDS = [
    ("help", "Lists all available commands."),
    ("command /?", "Shows help for a specific command."),
    ("dir", "Lists files and directories."),
    ("cd", "Changes directory."),
    ("copy", "Copies files."),
    ("move", "Moves files."),
    ("del", "Deletes files."),
    ("ipconfig", "Views network configuration."),
    ("ping", "Tests network connection."),
    ("cls", "Clears the screen."),
    ("tasklist", "Lists running processes."),
    ("mkdir", "Creates a directory."),
    ("rmdir", "Removes a directory."),
    ("ren", "Renames a file or directory."),
    ("type", "Displays the content of a file."),
    ("find", "Searches for a text string in a file."),
    ("date", "Displays or sets the date."),
    ("time", "Displays or sets the time."),
    ("echo", "Displays a message."),
    ("exit", "Exits the command prompt."),
    ("Get-Command", "Lists all available cmdlets."),
    ("Get-Help", "Displays help for a cmdlet."),
    ("Get-Process", "Gets running processes."),
    ("Get-Service", "Gets services."),
    ("Get-ChildItem", "Lists files and directories."),
    ("Copy-Item", "Copies items."),
    ("Move-Item", "Moves items."),
    ("Remove-Item", "Deletes items."),
    ("Rename-Item", "Renames items."),
    ("New-Item", "Creates a new item (file or directory)."),
    ("Set-Content", "Writes or replaces the content of a file."),
    ("Add-Content", "Appends content to a file."),
    ("Out-File", "Sends output to a file."),
    ("ConvertTo-Html", "Creates an HTML file from output."),
    ("Export-Csv", "Exports data to a CSV file."),
    ("Import-Csv", "Imports data from a CSV file."),
    ("Clear-History", "Clears command history."),
    ("Test-NetConnection", "Tests network connection."),
    ("Invoke-Command", "Runs commands on local or remote computers."),
    ("Set-ExecutionPolicy", "Changes the execution policy."),
    ("New-Alias", "Creates a new alias.")
]

class VamShellApp:
    def __init__(self, root):
        self.root = root
        self.root.title("VamShell")
        self.root.geometry("800x600")
        self.root.configure(bg="#1e1e1e")

        self.shell_type = tk.StringVar(value="cmd")
        self.command_var = tk.StringVar()

        # Shell type dropdown
        shell_dropdown = ttk.Combobox(root, values=["cmd", "powershell"], textvariable=self.shell_type)
        shell_dropdown.pack(pady=10)

        # Command dropdown with autocomplete
        self.command_combo = ttk.Combobox(root, values=[f"{cmd} - {desc}" for cmd, desc in COMMANDS], textvariable=self.command_var)
        self.command_combo.pack(fill="x", padx=10)

        # Run button
        run_button = ttk.Button(root, text="Run", command=self.run_command)
        run_button.pack(pady=5)

        # Output box
        self.output = scrolledtext.ScrolledText(root, bg="#252526", fg="white", insertbackground="white")
        self.output.pack(fill="both", expand=True, padx=10, pady=10)

    def run_command(self):
        command_text = self.command_var.get().split(" - ")[0].strip()
        shell = self.shell_type.get()

        if shell == "powershell":
            full_command = ["powershell", "-Command", command_text]
        else:
            full_command = command_text

        try:
            output = subprocess.check_output(full_command, shell=True, stderr=subprocess.STDOUT, text=True)
        except subprocess.CalledProcessError as e:
            output = e.output

        self.output.insert(tk.END, f"> {command_text}\n{output}\n")
        self.output.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = VamShellApp(root)
    root.mainloop()

