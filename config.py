import os
import logging
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "data")
LOG_DIR = os.path.join(BASE_DIR, "logs")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

DB_PATH = os.path.join(DATA_DIR, "saas.db")
OUTPUT_PATH = os.path.join(DATA_DIR, "relatorio_financeiro.xlsx")
LOG_PATH = os.path.join(LOG_DIR, "sistema.log")

# Mantido para compatibilidade com código legado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S',
    handlers=[
        logging.FileHandler(LOG_PATH, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

if __name__ == "__main__":
    print(f"📁 Pasta do Projeto: {BASE_DIR}")
    print(f"💾 Banco de Dados: {DB_PATH}")
    print(f"📝 Logs serão salvos em: {LOG_PATH}")
    print("✅ Configuração carregada com sucesso")