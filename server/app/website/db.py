import sqlite3

import sqlite3
import os
import io
import json

c, conn = None, None

def open_database():
    global c, conn
    conn = sqlite3.connect(os.path.join("app", "website", "data.db"), detect_types=sqlite3.PARSE_DECLTYPES)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users(username text, email text, password text)")
    c.execute("CREATE TABLE IF NOT EXISTS posts(id integer primary key autoincrement, json text)")

def check_for_username(username):
    # Checks if the username is already in the database
    c.execute("SELECT EXISTS(SELECT 1 FROM users WHERE username=?)", (username,))
    return c.fetchone() != (0,)

def check_for_email(email):
    # Checks if the username is already in the database
    c.execute("SELECT EXISTS(SELECT 1 FROM users WHERE email=?)", (email,))
    return c.fetchone() != (0,)

def get_user_info(email):
    # Returns user data from email
    c.execute("SELECT username, email, password FROM users WHERE email=?", (email,))
    return c.fetchone()

def add_user_to_database(username, email, password):
    global c, conn
    # Check if the password already exists in the database

    c.execute("INSERT INTO users (username, email, password) VALUES (?,?,?)", (username, email, password))
    conn.commit()
    return True

def add_post_to_database(post):
    # Adds te post dictionary to the database
    c.execute("INSERT INTO posts (json) VALUES (?)", (json.dumps(post),) )
    conn.commit()


def get_post_from_id(post_id):
    # Get the post from id
    c.execute("SELECT json FROM posts WHERE id=?", (post_id,) )
    return json.loads(c.fetchone()[0])


def set_post(post_id, updated_data):
    c.execute("UPDATE posts SET json=? WHERE id=?", (json.dumps(updated_data), post_id))
    conn.commit()


def get_all_posts():
    # Returns all the posts in the database
    c.execute("SELECT * FROM posts")
    posts = c.fetchall()
    return [(post_id, json.loads(j)) for post_id, j in posts][::-1]