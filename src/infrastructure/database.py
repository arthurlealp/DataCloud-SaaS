"""
Gerenciamento de conexões e operações de banco de dados.
Implementa context manager seguro e connection pooling.
"""

import sqlite3
import logging
from contextlib import contextmanager
from typing import Optional, Generator
from pathlib import Path


class DatabaseConnection:
    """
    Gerenciador de conexões com o banco de dados.
    
    Usa context manager para garantir que conexões sejam sempre fechadas.
    """
    
    def __init__(self, db_path: str):
        """
        Inicializa o gerenciador de conexões.
        
        Args:
            db_path: Caminho para o arquivo do banco SQLite.
        """
        self.db_path = db_path
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Garante que o diretório do banco existe."""
        db_file = Path(self.db_path)
        db_file.parent.mkdir(parents=True, exist_ok=True)
    
    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """
        Context manager para conexões seguras.
        
        Garante que:
        - Conexão é fechada após uso
        - Rollback em caso de erro
        - Logging de operações
        
        Yields:
            Conexão ativa com o banco.
            
        Example:
            >>> db = DatabaseConnection("data/saas.db")
            >>> with db.get_connection() as conn:
            ...     cursor = conn.cursor()
            ...     cursor.execute("SELECT * FROM planos")
        """
        conn = None
        try:
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            conn.row_factory = sqlite3.Row  # Permite acesso por nome de coluna
            
            logging.debug(f"Conexão aberta: {self.db_path}")
            yield conn
            
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
                logging.error(f"Erro no banco de dados, rollback executado: {e}")
            raise
            
        except Exception as e:
            if conn:
                conn.rollback()
            logging.error(f"Erro inesperado: {e}")
            raise
            
        finally:
            if conn:
                conn.close()
                logging.debug("Conexão fechada com segurança")
    
    def execute_query(self, query: str, params: tuple = ()) -> list:
        """
        Executa query SELECT retornando resultados.
        
        Args:
            query: SQL query a executar.
            params: Parâmetros da query (para queries parametrizadas).
            
        Returns:
            Lista de resultados.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def execute_command(self, command: str, params: tuple = ()) -> int:
        """
        Executa comando INSERT/UPDATE/DELETE.
        
        Args:
            command: SQL command a executar.
            params: Parâmetros do comando.
            
        Returns:
            ID da última linha inserida ou número de linhas afetadas.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(command, params)
            conn.commit()
            return cursor.lastrowid
    
    def execute_many(self, command: str, params_list: list) -> None:
        """
        Executa comando em lote (batch insert/update).
        
        Args:
            command: SQL command a executar.
            params_list: Lista de tuplas com parâmetros.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(command, params_list)
            conn.commit()
            logging.info(f"Executados {len(params_list)} comandos em lote")


# Singleton global para reutilização
_db_instance: Optional[DatabaseConnection] = None


def get_database(db_path: str) -> DatabaseConnection:
    """
    Retorna instância singleton do database.
    
    Args:
        db_path: Caminho do banco de dados.
        
    Returns:
        Instância do DatabaseConnection.
    """
    global _db_instance
    if _db_instance is None or _db_instance.db_path != db_path:
        _db_instance = DatabaseConnection(db_path)
    return _db_instance
