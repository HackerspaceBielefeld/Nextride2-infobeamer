import subprocess
import time
import os


def main():
    extensions_path = "extensions"
    extensions = os.listdir(extensions_path)

    for extension in extensions:
        extension_main_path = extensions_path + "/" + extension + "/main.py"
        commands = '''
        source ../.venv/bin/activate
        python {extension_main_path}
        '''
        process = subprocess.Popen('/bin/bash', stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        out, err = process.communicate(commands)
        print(out)
    
    time.sleep(600) #update the extensions every 10 min




main()