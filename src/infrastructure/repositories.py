"""
Repositórios para acesso a dados.
Implementa Repository Pattern para isolar lógica de acesso ao banco.
"""

import pandas as pd
import logging
from typing import Dict

from src.infrastructure.database import DatabaseConnection


class SQLiteAssinaturaRepository:
    """
    Implementação SQLite do repositório de assinaturas.
    
    Usa a View otimizada do banco para queries performáticas.
    """
    
    def __init__(self, db: DatabaseConnection):
        """
        Inicializa o repositório.
        
        Args:
            db: Instância do DatabaseConnection.
        """
        self.db = db
    
    def buscar_todas(self, validar: bool = False) -> pd.DataFrame:
        """
        Busca todas as assinaturas.
        
        Args:
            validar: Se True, valida dados (feature futura).
            
        Returns:
            DataFrame com todas as assinaturas.
        """
        query = """
            SELECT * FROM vw_assinaturas_detalhadas
            ORDER BY data_inicio DESC
        """
        
        with self.db.get_connection() as conn:
            df = pd.read_sql(query, conn)
            logging.info(f"Buscadas {len(df)} assinaturas")
            return df
    
    def buscar_por_status(self, status: str) -> pd.DataFrame:
        """
        Busca assinaturas por status específico.
        
        Args:
            status: Status desejado (Ativo, Cancelado, Trial, Inativo).
            
        Returns:
            DataFrame filtrado por status.
        """
        query = """
            SELECT * FROM vw_assinaturas_detalhadas
            WHERE status = ?
            ORDER BY data_inicio DESC
        """
        
        with self.db.get_connection() as conn:
            df = pd.read_sql(query, conn, params=(status,))
            logging.info(f"Buscadas {len(df)} assinaturas com status '{status}'")
            return df
    
    def contar_por_plano(self) -> Dict[str, int]:
        """
        Conta número de assinaturas por plano.
        
        Returns:
            Dicionário {nome_plano: contagem}.
        """
        query = """
            SELECT nome_plano, COUNT(*) as total
            FROM vw_assinaturas_detalhadas
            GROUP BY nome_plano
            ORDER BY total DESC
        """
        
        with self.db.get_connection() as conn:
            df =pd.read_sql(query, conn)
            resultado = dict(zip(df['nome_plano'], df['total']))
            logging.info(f"Contagem por plano: {resultado}")
            return resultado
