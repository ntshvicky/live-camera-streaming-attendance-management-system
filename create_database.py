import sqlite3
conn = sqlite3.connect('database.db')
c = conn.cursor()
sql = """
DROP TABLE IF EXISTS users;
CREATE TABLE users (
           id integer unique primary key autoincrement,
           name text
);
DROP TABLE IF EXISTS attendance;
CREATE TABLE attendance (
           id integer unique primary key autoincrement,
           user_id integer,
           attendance_date datetime not null default CURRENT_TIMESTAMP
);
"""
c.executescript(sql)
conn.commit()
conn.close()