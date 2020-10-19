import sqlite3
import numpy as np
import os
import io

c, conn = None, None

# Adapters
def adapt_array(array):
    out = io.BytesIO()
    np.save(out, array)
    out.seek(0)
    return sqlite3.Binary(out.read())

def convert_array(text):
    out = io.BytesIO(text)
    out.seek(0)
    return np.load(out)

sqlite3.register_adapter(np.ndarray, adapt_array)
sqlite3.register_converter("array", convert_array)
 
# Database functions
def open_database():
    global c, conn
    if c:
        return
    conn = sqlite3.connect(os.path.join("app", "database", "false.db"), check_same_thread=False, detect_types=sqlite3.PARSE_DECLTYPES)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS misinformationData(id integer primary key autoincrement, sentence text, link text, info text, start integer, end integer)")
    c.execute("CREATE TABLE IF NOT EXISTS vectorTable(id integer primary key autoincrement, vector array)")

def close_database():
    c.close()
    conn.close()

def insert_sentence_object(sentence, link, info, vectors):
    start = insert_vector(vectors[0])
    end = start
    for i in range(1, len(vectors)):
        end = insert_vector(vectors[i])
    c.execute("INSERT INTO misinformationData (sentence, link, info, start, end) VALUES (?,?,?,?,?)", (sentence, link, info, start, end))
    conn.commit()

def insert_vector(vector):
    """
    Adds a vector to the vector table
    """
    c.execute("INSERT INTO vectorTable (vector) VALUES (?)", (vector,))
    conn.commit()
    return c.lastrowid

def get_all_keys_and_vectors():
    return [pair for pair in c.execute("SELECT id, vector FROM vectorTable")]

def get_return_from_keys(keys):
    out = set()
    for key in keys:
        c.execute(f"SELECT sentence, link, info FROM misinformationData WHERE start <= ? AND end >= ?", (key,key))
        out.add(c.fetchone())
    return tuple(out)