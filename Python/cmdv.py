import sys
import os
import time as t
import signal

print(f"\rVahincmd -> {t.ctime()}")

def handler(signum, frame):
    if signum == signal.SIGBREAK:
        print("\nExiting...")
        sys.exit(0)

signal.signal(signal.SIGBREAK, handler)   # CTRL+Z on Windows

while True:
    command = input(f"{os.getcwd()}>>> ").strip()

    if command.lower() == "exit":
        break

    elif command.startswith("cd "):
        try:
            os.chdir(command[3:].strip())
        except Exception as e:
            print(f"Error: {e}")

    elif command:
        os.system(command)


