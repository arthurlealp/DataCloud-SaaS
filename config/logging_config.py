"""
Configuração avançada de logging para a aplicação.
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler


def setup_logging(
    log_level: str = "INFO",
    log_dir: str = "logs",
    log_file: str = "sistema.log"
):
    """
    Configura sistema de logging com rotação de arquivos.
    
    Args:
        log_level: Nível de log (DEBUG, INFO, WARNING, ERROR).
        log_dir: Diretório para salvar logs.
        log_file: Nome do arquivo de log.
    """
    # Garante que diretório existe
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    
    # Caminho completo do arquivo
    log_file_path = log_path / log_file
    
    # Formato das mensagens
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Configuração do root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove handlers existentes
    logger.handlers.clear()
    
    # Handler para arquivo com rotação (max 10MB, mantém 5 backups)
    file_handler = RotatingFileHandler(
        log_file_path,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(log_format, date_format))
    
    # Handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.setFormatter(logging.Formatter(log_format, date_format))
    
    # Adiciona handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    logging.info(f"Sistema de logging iniciado (nível: {log_level})")
    logging.info(f"Logs sendo salvos em: {log_file_path}")


# Configura stdout para UTF-8
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass
