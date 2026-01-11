import sys
import os
import shutil

def main():
    files = sys.argv[1:]
    if not files:
        input("No files provided. Drag files onto this program's icon. Press Enter to exit.")
        return
    
    new_ext = ".xlsm"           
    if not new_ext.startswith('.'):
        new_ext = '.' + new_ext

    for file_path in files:
        if not os.path.isfile(file_path):
            print(f"Skipping {file_path}: Not a valid file.")
            continue

        dir_name = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)
        root = os.path.splitext(file_name)[0]
        new_name = f"{root}{new_ext}"
        new_path = os.path.join(dir_name, new_name)

        # Handle existing files
        counter = 1
        while os.path.exists(new_path):
            new_name = f"{root}_{counter}{new_ext}"
            new_path = os.path.join(dir_name, new_name)
            counter += 1

        try:
            shutil.copy2(file_path, new_path)
            print(f"Created: {os.path.basename(new_path)}")
        except Exception as e:
            print(f"Failed to create {new_name}: {str(e)}")

    

if __name__ == "__main__":
    main()