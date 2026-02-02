import sqlite3
import pandas as pd
import logging
from config import DB_PATH, OUTPUT_PATH
import sys

sys.stdout.reconfigure(encoding='utf-8')

class SaasETL:
    def __init__(self):
        """Construtor: Prepara o terreno."""
        self.conn = None
    
    def conectar(self):
        """Passo 1: Abre a porta do banco de dados."""
        try:
            self.conn = sqlite3.connect(DB_PATH)
            logging.info(f"🔌 Conectado ao banco: {DB_PATH}")
        except Exception as e:
            logging.error(f"❌ Erro ao conectar: {e}")
            raise

    def extrair(self):
        """Passo 2: EXTRACT (SQL) - Consome a View pronta do Banco."""
        if not self.conn:
            self.conectar()
        
        # REFATORADO: Agora pedimos apenas a View. 
        # O banco já processou os JOINs e os índices.
        query = "SELECT * FROM vw_assinaturas_detalhadas"
        
        try:
            logging.info("📥 Iniciando extração de dados (View)...")
            df = pd.read_sql(query, self.conn)
            logging.info(f"✅ Dados extraídos. {len(df)} registros encontrados.")
            return df
        except Exception as e:
            logging.error(f"❌ Falha na extração SQL: {e}")
            return pd.DataFrame()

    def transformar(self, df):
        """Passo 3: TRANSFORM (Pandas) - Gera inteligência de negócio."""
        if df.empty:
            logging.warning("⚠️ DataFrame vazio. Pulando transformação.")
            return df

        logging.info("🔄 Iniciando transformações e cálculos de KPIs...")

        try:
            # 1. Converter datas (SQLite entrega como texto)
            # Garantimos que as colunas existem na View antes de converter
            if 'data_inicio' in df.columns:
                df['data_inicio'] = pd.to_datetime(df['data_inicio'])
            
            # 2. KPI: Tempo de Casa (Em dias)
            agora = pd.Timestamp.now()
            df['dias_de_cliente'] = (agora - df['data_inicio']).dt.days

            # 3. KPI: LTV (Lifetime Value) - Quanto o cliente já gastou?
            # Fórmula: (Meses de casa) * Valor do Plano
            df['LTV_Estimado'] = (df['dias_de_cliente'] / 30) * df['preco_mensal']
            df['LTV_Estimado'] = df['LTV_Estimado'].round(2)

            logging.info("✅ Transformação concluída.")
            return df
        except Exception as e:
            logging.error(f"❌ Erro na transformação: {e}")
            return df

    def carregar(self, df):
        """Passo 4: LOAD (Excel) - Salva o resultado final."""
        try:
            logging.info(f"💾 Salvando relatório em: {OUTPUT_PATH}")
            df.to_excel(OUTPUT_PATH, index=False)
            logging.info("🚀 Relatório gerado com sucesso!")
        except Exception as e:
            logging.error(f"❌ Erro ao salvar Excel: {e}")

    def fechar(self):
        """Limpeza: Fecha a conexão."""
        if self.conn:
            self.conn.close()
            logging.info("🔒 Conexão com o banco fechada.")