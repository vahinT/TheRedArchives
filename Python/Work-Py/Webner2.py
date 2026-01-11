import webbrowser

print("Welcome to Webner2!")
print()
print("By --- Vahin Vamsidhar Masavarapu")
print()
print("Webner opens webpages using URLs given by the user")
print()

while True:
    url = input("URL>>> ")
    print()

    if url.lower() in ["exit", "quit"]:
        break  # Exit the loop

    try:
        webbrowser.open_new(url)
    except Exception as e:
        print(f"Error: {str(e)}")
        print("Please enter a valid URL.")