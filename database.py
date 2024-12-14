import sqlite3

conn = sqlite3.connect('content_generation.db')
cursor = conn.cursor()


cursor.execute("SELECT * FROM generated_content")
rows = cursor.fetchall()

print("Generated Content Table:")
for row in rows:
    print(row)

conn.close()
