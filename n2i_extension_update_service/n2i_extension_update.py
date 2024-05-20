import subprocess
import time
import os


def main():
    extensions_path = "extensions"
    extensions = os.listdir(extensions_path)

    for extension in extensions:
        extension_main_path = extensions_path + "/" + extension + "/main.py"
        subprocess.run(["python", extension_main_path])
    
    time.sleep(600) #update the extensions every 10 min

main()