import sqlite3
import os

from helper import logging

def init_table(conn):
    """ Create a database connection to a SQLite database """

    sql_create_config_table = """
                            CREATE TABLE IF NOT EXISTS CMSConfig (
                            id INTEGER PRIMARY KEY,
                            name TEXT NOT NULL,
                            active BOOLEAN NOT NULL
                            );
                            """
    
    sql_add_config_entries = """
                            INSERT INTO CMSConfig (name, active)
                            VALUES (?, ?)
                            """


    # CMS Config
    config = [
        ('login', True),
        ('approve', True),
        ('email_approve', False)
    ]

    cur = conn.cursor()
    try:
        cur.execute(sql_create_config_table)
        cur.executemany(sql_add_config_entries, config)
        conn.commit()
        logging("CMSConfig table created successfully")
    except sqlite3.Error as e:
        logging(e)

def get_conn():
    db_dir = "./extensions/cms/instance"
    db_path = os.path.join(db_dir, "cms.db")

    create_table = False
    if not os.path.exists(db_path):
        os.makedirs(db_dir, exist_ok=True)
        create_table = True

    try:
        conn = sqlite3.connect(db_path)
    except sqlite3.Error as e:
        logging(f"Error connecting to database: {e}")
        return None

    if create_table:
        init_table(conn)

    return conn

class CMSConfig:
    def __init__(self, _id:int, _name:str, _active:bool):
        self.id = _id
        self.name = _name
        self.active = _active

    def activate(self):
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
                        UPDATE CMSConfig
                        SET active = ?
                        WHERE id = ?
                        """, (True, self.id))        
        conn.commit()
        conn.close()
    
    def deactivate(self):
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
                        UPDATE CMSConfig
                        SET active = ?
                        WHERE id = ?
                        """, (False, self.id))        
        conn.commit()
        conn.close()


def get_cms_config():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM CMSConfig")
    rows = cur.fetchall()
    conn.close()

    if not rows: return None

    cms_config = []
    for row in rows:
        cms_config.append(CMSConfig(row[0], row[1], row[2]))
    return cms_config

def get_setting_from_config(name:str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM CMSConfig WHERE name = ?", (name,))
    row = cur.fetchone()
    conn.close()

    setting = CMSConfig(row[0], row[1], row[2])

    return setting