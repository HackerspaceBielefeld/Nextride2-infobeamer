import subprocess
import time
import os

from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base


Base = declarative_base()

class Extension(Base):
    __tablename__ = 'extension'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    managable = Column(Boolean, nullable=False)
    active = Column(Boolean, nullable=False)

def check_extensions_active(extension_name: str):
    # Replace 'sqlite:///path/to/your_database.db' with your actual database URL
    DATABASE_URL = 'sqlite:///instance/uploads.sqlite'
    # Create an engine
    engine = create_engine(DATABASE_URL)
    # Create a configured "Session" class
    Session = sessionmaker(bind=engine)
    session = Session()

    extension = session.query(Extension).filter(Extension.name == extension_name).first()

    session.close()

    # Check if the extension was found and print it
    if extension.active:
        return True
    return False


def main():
    extensions_path = "extensions"
    extensions = os.listdir(extensions_path)

    for extension in extensions:
        if not check_extensions_active(extension):
            continue

        extension_main_path = extensions_path + "/" + extension + "/main.py"
        commands = f'''
        source ../.venv/bin/activate
        python3 {extension_main_path}
        '''
        with subprocess.Popen('/bin/bash', stdin=subprocess.PIPE, \
                                    stdout=subprocess.PIPE, text=True) as process:
            out, err = process.communicate(commands)
            print(out)
            print(err)

    time.sleep(600) #update the extensions every 10 min


if __name__ == "__main__":
    main()
