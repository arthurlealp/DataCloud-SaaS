"""
Script CLI para executar pipeline ETL.
Usa arquitetura refatorada com serviços.
"""

from src.application.etl_service import SaasETLService
from config.logging_config import setup_logging
from config.settings import settings
import logging


def rodar_pipeline():
    """Executa pipeline ETL completo."""
    # Configura logging
    setup_logging(
        log_level=settings.LOG_LEVEL,
        log_dir=settings.LOG_DIR
    )
    
    print("\n" + "="*60)
    print("🚀 DATACLOUD SAAS - PIPELINE ETL")
    print("="*60 + "\n")
    
    try:
        # Instancia serviço ETL
        etl = SaasETLService()
        
        # Executa pipeline completo
        dados = etl.executar_pipeline_completo()
        
        if dados is not None:
            print("\n" + "-"*60)
            print(f"✅ Pipeline concluído com sucesso!")
            print(f"📊 {len(dados)} registros processados")
            print(f"💾 Relatório salvo em: {settings.get_output_path_absolute()}")
            print("-"*60 + "\n")
        else:
            print("\n⚠️ Pipeline finalizado sem gerar dados\n")
            
    except Exception as e:
        logging.error(f"Erro crítico no pipeline: {e}", exc_info=True)
        print(f"\n❌ Erro: {e}\n")


if __name__ == "__main__":
    rodar_pipeline()