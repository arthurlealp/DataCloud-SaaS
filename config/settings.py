"""
Configurações da aplicação baseadas em ambiente.
Usa Pydantic Settings para validação e carregamento de .env
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path
from typing import Literal, List
import os


class Settings(BaseSettings):
    """
    Configurações centralizadas da aplicação.
    
    Carrega valores de variáveis de ambiente ou .env file.
    """
    
    # === Ambiente ===
    ENV: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Ambiente de execução"
    )
    DEBUG: bool = Field(
        default=True,
        description="Modo debug ativo"
    )
    
    # === Banco de Dados ===
    DB_TYPE: Literal["sqlite", "postgresql"] = Field(
        default="sqlite",
        description="Tipo de banco de dados"
    )
    DB_PATH: str = Field(
        default="data/saas.db",
        description="Caminho do banco SQLite"
    )
    DB_TIMEOUT: int = Field(
        default=30,
        description="Timeout de conexão em segundos"
    )
    
    # === ETL ===
    BATCH_SIZE: int = Field(
        default=1000,
        description="Tamanho do lote para processamento"
    )
    CACHE_TTL: int = Field(
        default=300,
        description="TTL do cache em segundos (5 minutos)"
    )
    
    # === Dashboard ===
    DASHBOARD_TITLE: str = Field(
        default="DataCloud SaaS Analytics",
        description="Título do dashboard"
    )
    REQUIRE_AUTH: bool = Field(
        default=False,
        description="Exigir autenticação no dashboard"
    )
    PAGE_SIZE: int = Field(
        default=50,
        description="Registros por página na paginação"
    )
    
    # === KPIs e Metas ===
    META_RECEITA_MENSAL: float = Field(
        default=60000.00,
        description="Meta de receita mensal (MRR)"
    )
    META_CHURN_MAX: float = Field(
        default=0.05,
        description="Taxa máxima aceitável de churn (5%)"
    )
    META_LTV_MINIMO: float = Field(
        default=1000.00,
        description="LTV mínimo esperado por cliente"
    )
    
    # === Segurança ===
    SECRET_KEY: str = Field(
        default="change-me-in-production-super-secret-key-2026",
        description="Chave secreta para criptografia"
    )
    ALLOWED_HOSTS: List[str] = Field(
        default=["localhost", "127.0.0.1", "0.0.0.0"],
        description="Hosts permitidos"
    )
    
    # === Logging ===
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO",
        description="Nível de logging"
    )
    LOG_DIR: str = Field(
        default="logs",
        description="Diretório para arquivos de log"
    )
    
    # === Paths ===
    BASE_DIR: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent,
        description="Diretório base do projeto"
    )
    DATA_DIR: str = Field(
        default="data",
        description="Diretório para arquivos de dados"
    )
    OUTPUT_PATH: str = Field(
        default="data/relatorio_financeiro.xlsx",
        description="Caminho do relatório Excel gerado"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    def get_db_path_absolute(self) -> str:
        """Retorna caminho absoluto do banco de dados."""
        if os.path.isabs(self.DB_PATH):
            return self.DB_PATH
        return str(self.BASE_DIR / self.DB_PATH)
    
    def get_output_path_absolute(self) -> str:
        """Retorna caminho absoluto do arquivo de saída."""
        if os.path.isabs(self.OUTPUT_PATH):
            return self.OUTPUT_PATH
        return str(self.BASE_DIR / self.OUTPUT_PATH)
    
    def ensure_directories(self):
        """Cria diretórios necessários se não existirem."""
        dirs_to_create = [
            self.BASE_DIR / self.DATA_DIR,
            self.BASE_DIR / self.LOG_DIR,
        ]
        
        for directory in dirs_to_create:
            directory.mkdir(parents=True, exist_ok=True)


# Singleton - instância global
settings = Settings()

# Garante que diretórios existem
settings.ensure_directories()
