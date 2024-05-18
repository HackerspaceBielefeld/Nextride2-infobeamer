import sqlite3
import os

class Tag:
    def __init__(self, id, name, limit):
        self.id = id
        self.name = name
        self.limit = limit
    
    def set_limit(self, new_limit: int):
        self.limit = new_limit
        
        # Update the limit in the database
        conn = get_conn()
        cur = conn.cursor()
        cur.execute('UPDATE tags SET tag_limit = ? WHERE id = ?', (self.limit, self.id))
        conn.commit()
        conn.close()

def init_table(conn):
    """ Create a database connection to a SQLite database """

    sql_create_tags_table = """ CREATE TABLE IF NOT EXISTS Tags (
                                    id INTEGER PRIMARY KEY,
                                    name TEXT NOT NULL UNIQUE,
                                    tag_limit INTEGER NOT NULL
                                ); """

    try:
        c = conn.cursor()
        c.execute(sql_create_tags_table)
        print("Tags table created successfully")
    except sqlite3.Error as e:
        print(e)

    return conn

def get_conn():
    # Determine the current working directory
    current_dir = os.getcwd()

    # Set the database path based on the context
    if current_dir.endswith('/html/extensions/mastodon'):
        db_path = "./instance/mastodon.db"
    else:
        db_path = "./extensions/mastodon/instance/mastodon.db"


    create_table = False
    if not os.path.exists(db_path):
        create_table = True

    conn = None
    try:
        conn = sqlite3.connect(db_path)
    except sqlite3.Error as e:
        print(e)

    if create_table:
        init_table(conn)

    return conn

def get_mastodon_tag_by_name(tag_name: str):
    conn = get_conn()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM Tags WHERE name=?", (tag_name,))
    row = cur.fetchone()
    if row:
        tag = Tag(row[0], row[1], row[2])
        return tag
    else:
        return None

def get_all_mastodon_tags():
    """ Query all tags from the Tags table """
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Tags")
    
    rows = cur.fetchall()
    conn.close()
    tags = []
    
    for row in rows:
        tag = Tag(row[0], row[1], row[2])
        tags.append(tag)
    
    return tags

def add_mastodon_tag(tag_name: str, tag_limit: int):
    """ Add a new tag to the Tags table """
    conn = get_conn()
    if get_mastodon_tag_by_name(tag_name):
        return False

    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO Tags (name, tag_limit) VALUES (?, ?)", (tag_name, tag_limit))
        conn.commit()
    except sqlite3.Error as e:
        return False
    return True

def remove_mastodon_tag(tag_name: str):
    """ Remove a tag from the Tags table by name """
    tag = get_mastodon_tag_by_name(tag_name)
    conn = get_conn()
    cur = conn.cursor()
    try:
        if tag:
            cur.execute("DELETE FROM Tags WHERE name=?", (tag_name,))
            conn.commit()
            return tag
        else:
            return False
    except sqlite3.Error as e:
        return False

def update_mastodon_tag(tag_name: str, tag_limit: int):
    tag = get_mastodon_tag_by_name(tag_name)
    if not tag:
        return False
    
    if tag_limit == 0:
        if not remove_mastodon_tag(tag_name):
            return False
    elif not tag.set_limit(tag_limit):
        return False
    return True

