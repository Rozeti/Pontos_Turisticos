import sqlite3

conn = sqlite3.connect("acessibilidade_turismo.db")
cursor = conn.cursor()

print("\n--- PONTOS TURÍSTICOS ---")
for row in cursor.execute("SELECT * FROM ponto_turistico"):
    print(row)

print("\n--- DADOS DE ACESSIBILIDADE ---")
for row in cursor.execute("SELECT * FROM acessibilidade"):
    print(row)

conn.close()
