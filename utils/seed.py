import sqlite3
import random
from datetime import datetime, timedelta
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

pasta_atual = os.path.dirname(os.path.abspath(__file__))
raiz_projeto = os.path.dirname(pasta_atual)
caminho_banco = os.path.join(raiz_projeto, "data", "saas.db")

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

# 🏖️ Nomes inspirados em Recife, PE
prefixos = [
    # Praias e lugares famosos
    "Boa Viagem", "Pina", "Brasília Teimosa", "Piedade", "Candeias",
    "Marco Zero", "Recife Antigo", "São José", "Santo Antônio",
    # Bairros icônicos
    "Casa Forte", "Espinheiro", "Graças", "Aflitos", "Derby",
    # Pontos turísticos
    "Paço Alfândega", "Torre Malakoff", "Kahal Zur Israel",
    # Referências culturais
    "Frevo", "Maracatu", "Manguebeat", "Boneco Gigante",
    # Tech + Regional
    "RecifeTech", "PortoDigital", "Mangue", "Capibaribe"
]

sufixos = [
    "Solutions", "Analytics", "Tech", "Digital", "Sistemas",
    "Labs", "Software", "Cloud", "Data", "Innovation",
    "Tecnologia", "Soluções", "LTDA", "S.A."
]

nomes_pessoas = [
    # Nomes comuns em Recife/PE
    "Arthur", "José", "Maria", "João", "Ana", 
    "Francisco", "Pedro", "Antônio", "Carlos", "Paulo",
    "Fernanda", "Juliana", "Beatriz", "Gabriela", "Larissa"
]

for i in range(1, 101):
    nome_empresa = f"{random.choice(prefixos)} {random.choice(sufixos)}"
    cnpj_fake = f"{random.randint(10000000, 99999999)}0001{random.randint(10,99)}"
    
    dias_atras = random.randint(1, 730)
    data_criacao = datetime.now() - timedelta(days=dias_atras)
    
    cursor.execute("INSERT INTO empresas (razao_social, cnpj, data_criacao) VALUES (?, ?, ?)", 
                   (nome_empresa, cnpj_fake, str(data_criacao.date())))
    
    id_empresa = cursor.lastrowid


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