import sqlite3
import random
from datetime import datetime, timedelta
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

pasta_atual = os.path.dirname(os.path.abspath(__file__))
caminho_banco = os.path.join(pasta_atual, "saas.db") 

print(f"🔍 Conectando no banco em: {caminho_banco}")

conexao = sqlite3.connect(caminho_banco) 
cursor = conexao.cursor()

print("🌱 Iniciando o povoamento do banco...")

planos = [
    (1, 'Basic', 99.90, 3, 50.0),
    (2, 'Pro', 199.90, 10, 500.0),
    (3, 'Enterprise', 499.90, 999, 5000.0)
]
try:
    cursor.executemany("INSERT OR IGNORE INTO planos VALUES (?,?,?,?,?)", planos)
    print("✅ Planos criados.")
except Exception as e:
    print(f"Aviso nos planos: {e}")

prefixos = ["Tech", "Soft", "Data", "Cloud", "Inova", "Web", "Net", "Sys"]
sufixos = ["Solutions", "Sistemas", "Ltda", "S.A.", "Digital", "Analytics"]
nomes_pessoas = ["Arthur", "Ana", "Bruno", "Carla", "Daniel", "Elena", "Fabio", "Gabriela"]
for i in range(1, 101):
    nome_empresa = f"{random.choice(prefixos)} {random.choice(sufixos)} {random.randint(1,999)}"
    cnpj_fake = f"{random.randint(10000000, 99999999)}0001{random.randint(10,99)}"
    
    dias_atras = random.randint(1, 730)
    data_criacao = datetime.now() - timedelta(days=dias_atras)
    
    cursor.execute("INSERT INTO empresas (razao_social, cnpj, data_criacao) VALUES (?, ?, ?)", 
                   (nome_empresa, cnpj_fake, str(data_criacao.date())))
    
    id_empresa = cursor.lastrowid

    nome_user = f"{random.choice(nomes_pessoas)} {random.choice(['Silva', 'Santos', 'Oliveira'])}"
    nome_user_clean = nome_user.split()[0].lower()
    email_user = f"{nome_user_clean}.{id_empresa}@example.com"
    
    cursor.execute("""
        INSERT INTO usuarios (nome, email, cargo, empresa_id) 
        VALUES (?, ?, ?, ?)""", 
        (nome_user, email_user, "Admin", id_empresa))

    status = random.choices(['Ativo', 'Cancelado', 'Trial', 'Inativo'], weights=[70, 10, 15, 5])[0]
    id_plano = random.randint(1, 3) 
    
    data_inicio = data_criacao
    data_renovacao = data_inicio + timedelta(days=30)
    proxima_cobranca = data_renovacao
    
    cursor.execute("""
        INSERT INTO assinaturas (status, data_inicio, data_renovacao, proxima_cobranca, empresa_id, plano_id)
        VALUES (?, ?, ?, ?, ?, ?)""",
        (status, str(data_inicio.date()), str(data_renovacao.date()), str(proxima_cobranca.date()), id_empresa, id_plano))

conexao.commit()
conexao.close()
print("🚀 Sucesso! 100 empresas e contratos gerados.")