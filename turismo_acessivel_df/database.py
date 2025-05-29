import sqlite3

def criar_banco():
    conn = sqlite3.connect('acessibilidade_turismo.db')
    cursor = conn.cursor()

    # Criação das tabelas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ponto_turistico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            descricao TEXT,
            endereco TEXT,
            latitude REAL,
            longitude REAL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS acessibilidade (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ponto_id INTEGER,
            rampa BOOLEAN,
            banheiro_adaptado BOOLEAN,
            sinalizacao_visual BOOLEAN,
            audiodescricao BOOLEAN,
            observacoes TEXT,
            origem TEXT,
            data_coleta DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (ponto_id) REFERENCES ponto_turistico(id)
        )
    ''')

    conn.commit()
    conn.close()
    print("Banco de dados criado com sucesso!")

if __name__ == "__main__":
    criar_banco()
