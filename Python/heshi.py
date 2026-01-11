from colorama import init, Fore, Style

# Initialize colorama
init()

print('Vahin\'s python REPL')

while True:
    try:
        command = input(Fore.MAGENTA + ">>> " + Style.RESET_ALL)  # PURPLE input prompt
        if command.lower() in ['exit', 'quit']:
            break
        exec(command)
    except Exception as e:
        print("Error:", e)
