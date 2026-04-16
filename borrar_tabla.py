import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()
cursor.execute('DROP TABLE IF EXISTS user;')
conn.commit()
conn.close()
print("Tabla 'user' eliminada.")