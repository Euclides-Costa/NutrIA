# perfil_db.py
import sqlite3
import json

def init_db():
    """Cria o banco de dados e a tabela de usuários se não existirem."""
    conn = sqlite3.connect('nutria.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            idade INTEGER,
            peso REAL,
            altura REAL,
            objetivo TEXT,
            restricoes TEXT,
            metas_json TEXT
        )
    ''')
    conn.commit()
    conn.close()

def calcular_metas_iniciais(peso: float, objetivo: str) -> dict:
    """Calcula uma meta diária simplificada com base no peso e objetivo."""
    # Cálculo base de calorias (Regra de bolso esportiva)
    if objetivo == 'emagrecer':
        kcal = peso * 25
    elif objetivo == 'ganhar':
        kcal = peso * 35
    else:
        kcal = peso * 30 # manter

    # Divisão de macros: 2g proteína/kg, 1g gordura/kg, resto em carboidrato
    proteina = peso * 2.0
    gordura = peso * 1.0
    carboidrato = (kcal - (proteina * 4) - (gordura * 9)) / 4

    return {
        "calorias": round(kcal),
        "proteinas_g": round(proteina),
        "carboidratos_g": round(carboidrato),
        "gorduras_g": round(gordura)
    }

def criar_perfil(nome: str, idade: int, peso: float, altura: float, objetivo: str, restricoes: list):
    """Salva o novo usuário no banco de dados."""
    metas = calcular_metas_iniciais(peso, objetivo)
    
    conn = sqlite3.connect('nutria.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO usuarios (nome, idade, peso, altura, objetivo, restricoes, metas_json)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (nome, idade, peso, altura, objetivo, json.dumps(restricoes), json.dumps(metas)))
    
    user_id = c.lastrowid
    conn.commit()
    conn.close()
    return user_id

def obter_perfil_usuario(user_id: int):
    """Busca o usuário no banco. Retorna None se não existir."""
    conn = sqlite3.connect('nutria.db')
    c = conn.cursor()
    c.execute('SELECT nome, metas_json, restricoes FROM usuarios WHERE id = ?', (user_id,))
    row = c.fetchone()
    conn.close()

    if row:
        return {
            "user_id": user_id,
            "nome": row[0],
            "metas_diarias": json.loads(row[1]),
            "restricoes": json.loads(row[2]),
            "historico_consumido_hoje": { 
                # Para simplificar o teste de hoje, começamos o dia com 0 consumido.
                "calorias": 0, "proteinas_g": 0, "carboidratos_g": 0, "gorduras_g": 0
            }
        }
    return None