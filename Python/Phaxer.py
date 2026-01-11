import os
import sys
import zipfile

def zip_folder_to_phax(folder_path):
    folder_path = os.path.abspath(folder_path)
    zip_name = folder_path + ".zip"
    
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, folder_path)
                zipf.write(abs_path, arcname=rel_path)
    
    phax_name = zip_name.replace(".zip", ".phax")
    os.rename(zip_name, phax_name)


def unzip_phax_file(phax_path):
    phax_path = os.path.abspath(phax_path)
    if not phax_path.endswith(".phax"):
        print("❌ Not a .phax file.")
        return

    zip_path = phax_path.replace(".phax", ".zip")
    os.rename(phax_path, zip_path)

    extract_dir = zip_path.replace(".zip", "_unzipped")

    with zipfile.ZipFile(zip_path, 'r') as zipf:
        zipf.extractall(extract_dir)

    os.remove(zip_path)
    print(f"✅ Extracted to: {extract_dir}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\n📦 Drag a folder or .phax file onto this script to use it.\n")
        input("Press Enter to close...")
    else:
        for path in sys.argv[1:]:
            if os.path.isdir(path):
                print(f"\n📁 Zipping folder: {path}")
                zip_folder_to_phax(path)
            elif path.endswith(".phax") and os.path.isfile(path):
                print(f"\n📄 Unzipping .phax file: {path}")
                unzip_phax_file(path)
            else:
                print(f"\n❓ Skipping unknown type: {path}")
