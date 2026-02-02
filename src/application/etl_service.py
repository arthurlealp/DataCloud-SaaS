"""
Serviço ETL refatorado usando nova arquitetura.
Integra repositórios, validação e cálculo de KPIs.
"""

import pandas as pd
import logging
from typing import Optional

from src.infrastructure.database import get_database
from src.infrastructure.repositories import SQLiteAssinaturaRepository
from src.application.kpi_calculator import KPICalculator
from config.settings import settings


class SaasETLService:
    """
    Serviço ETL refatorado com Clean Architecture.
    
    Separa responsabilidades e usa repositórios para acesso a dados.
    """
    
    def __init__(self):
        """Inicializa o serviço ETL."""
        self.db = get_database(settings.get_db_path_absolute())
        self.repository = SQLiteAssinaturaRepository(self.db)
        logging.info("ETL Service inicializado")
    
    def extrair(self, validar: bool = True) -> pd.DataFrame:
        """
        Extrai dados do banco usando repository.
        
        Args:
            validar: Se True, valida dados usando Pydantic.
            
        Returns:
            DataFrame com dados extraídos.
        """
        try:
            logging.info("📥 Iniciando extração de dados...")
            df = self.repository.buscar_todas(validar=validar)
            logging.info(f"✅ Extração concluída. {len(df)} registros")
            return df
        except Exception as e:
            logging.error(f"❌ Erro na extração: {e}")
            return pd.DataFrame()
    
    def transformar(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transforma dados e calcula KPIs.
        
        Args:
            df: DataFrame bruto.
            
        Returns:
            DataFrame transformado com KPIs calculados.
        """
        if df.empty:
            logging.warning("⚠️ DataFrame vazio, pulando transformação")
            return df
        
        try:
            logging.info("🔄 Iniciando transformações...")
            
            # Converte datas
            if 'data_inicio' in df.columns:
                df['data_inicio'] = pd.to_datetime(df['data_inicio'])
            
            if 'proxima_cobranca' in df.columns:
                df['proxima_cobranca'] = pd.to_datetime(df['proxima_cobranca'], errors='coerce')
            
            # Calcula KPIs usando serviço
            df = KPICalculator.calcular_ltv(df)
            
            logging.info("✅ Transformação concluída")
            return df
            
        except Exception as e:
            logging.error(f"❌ Erro na transformação: {e}")
            return df
    
    def carregar(self, df: pd.DataFrame, caminho: Optional[str] = None) -> bool:
        """
        Salva dados transformados em Excel.
        
        Args:
            df: DataFrame a salvar.
            caminho: Caminho do arquivo. Se None, usa configuração padrão.
            
        Returns:
            True se salvou com sucesso.
        """
        if df.empty:
            logging.warning("⚠️ DataFrame vazio, nada para salvar")
            return False
        
        try:
            if caminho is None:
                caminho = settings.get_output_path_absolute()
            logging.info(f"💾 Salvando relatório em: {caminho}")
            df.to_excel(caminho, index=False)
            logging.info("🚀 Relatório gerado com sucesso!")
            return True
            
        except Exception as e:
            logging.error(f"❌ Erro ao salvar: {e}")
            return False
    
    def executar_pipeline_completo(self) -> Optional[pd.DataFrame]:
        """
        Executa ETL completo: Extract -> Transform -> Load.
        
        Returns:
            DataFrame final ou None em caso de erro.
        """
        logging.info("🚀 Iniciando pipeline ETL completo")
        
        try:
            # Extract
            dados = self.extrair(validar=True)
            if dados.empty:
                logging.warning("Sem dados para processar")
                return None
            
            # Transform
            dados_tratados = self.transformar(dados)
            
            # Load
            sucesso = self.carregar(dados_tratados)
            
            if sucesso:
                logging.info("✅ Pipeline ETL concluído com sucesso")
                return dados_tratados
            else:
                logging.error("❌ Falha ao salvar dados")
                return None
                
        except Exception as e:
            logging.error(f"❌ Erro crítico no pipeline: {e}")
            return None
