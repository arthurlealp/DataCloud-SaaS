"""
Sistema de alertas automáticos para monitoramento.
Detecta anomalias e condições críticas no negócio.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List
import pandas as pd
import logging


class TipoAlerta(Enum):
    """Tipos de alertas por severidade."""
    INFO = "ℹ️"
    ATENCAO = "⚠️"
    CRITICO = "🚨"


@dataclass
class Alerta:
    """Estrutura de um alerta."""
    tipo: TipoAlerta
    titulo: str
    mensagem: str
    metrica_atual: float
    limite: float
    
    def to_dict(self) -> dict:
        """Converte alerta para dicionário."""
        return {
            'tipo': self.tipo.value,
            'titulo': self.titulo,
            'mensagem': self.mensagem,
            'metrica_atual': self.metrica_atual,
            'limite': self.limite
        }


class AlertaService:
    """
    Serviço de monitoramento e alertas automáticos.
    
    Detecta condições anormais e gera alertas para o dashboard.
    """
    
    def __init__(self, config):
        """
        Inicializa o serviço de alertas.
        
        Args:
            config: Objeto Settings com configurações.
        """
        self.config = config
        self.alertas: List[Alerta] = []
    
    def verificar_alertas(self, df: pd.DataFrame) -> List[Alerta]:
        """
        Verifica todas as condições de alerta.
        
        Args:
            df: DataFrame com dados de assinaturas.
            
        Returns:
            Lista de alertas detectados.
        """
        self.alertas = []
        
        if df.empty:
            logging.warning("DataFrame vazio, sem alertas gerados")
            return self.alertas
        
        # Verifica cada condição
        self._verificar_churn(df)
        self._verificar_receita(df)
        self._verificar_ltv_baixo(df)
        self._verificar_trial_expirados(df)
        
        logging.info(f"Total de {len(self.alertas)} alertas gerados")
        return self.alertas
    
    def _verificar_churn(self, df: pd.DataFrame):
        """Verifica se taxa de churn está crítica."""
        total_clientes = len(df)
        if total_clientes == 0:
            return
        
        churn_count = len(df[df['status'] == 'Cancelado'])
        taxa_churn = churn_count / total_clientes
        
        limite = self.config.META_CHURN_MAX
        
        if taxa_churn > limite:
            self.alertas.append(Alerta(
                tipo=TipoAlerta.CRITICO,
                titulo="Taxa de Churn Crítica",
                mensagem=(
                    f"Churn de {taxa_churn:.1%} está acima da meta de {limite:.1%}. "
                    f"{churn_count} clientes cancelados!"
                ),
                metrica_atual=taxa_churn,
                limite=limite
            ))
        elif taxa_churn > (limite * 0.8):
            # Alerta de atenção se estiver próximo do limite
            self.alertas.append(Alerta(
                tipo=TipoAlerta.ATENCAO,
                titulo="Churn Próximo ao Limite",
                mensagem=(
                    f"Taxa de churn ({taxa_churn:.1%}) está se aproximando do limite "
                    f"máximo ({limite:.1%})"
                ),
                metrica_atual=taxa_churn,
                limite=limite
            ))
    
    def _verificar_receita(self, df: pd.DataFrame):
        """Verifica se MRR está abaixo da meta."""
        # Exclui cancelados do cálculo de MRR
        df_ativos = df[df['status'] != 'Cancelado']
        mrr_atual = df_ativos['preco_mensal'].sum()
        meta = self.config.META_RECEITA_MENSAL
        
        if mrr_atual < meta:
            deficit = meta - mrr_atual
            percentual_deficit = (deficit / meta) * 100
            
            if percentual_deficit > 20:
                tipo = TipoAlerta.CRITICO
                titulo = "Meta de Receita Crítica"
            else:
                tipo = TipoAlerta.ATENCAO
                titulo = "Meta de Receita não Atingida"
            
            self.alertas.append(Alerta(
                tipo=tipo,
                titulo=titulo,
                mensagem=(
                    f"MRR atual (R$ {mrr_atual:,.2f}) está R$ {deficit:,.2f} "
                    f"abaixo da meta (R$ {meta:,.2f})"
                ),
                metrica_atual=mrr_atual,
                limite=meta
            ))
        elif mrr_atual >= meta * 1.2:
            # Alerta positivo se ultrapassar meta em 20%
            self.alertas.append(Alerta(
                tipo=TipoAlerta.INFO,
                titulo="Meta de Receita Superada! 🎉",
                mensagem=(
                    f"Parabéns! MRR atual (R$ {mrr_atual:,.2f}) está "
                    f"{((mrr_atual/meta - 1) * 100):.1f}% acima da meta!"
                ),
                metrica_atual=mrr_atual,
                limite=meta
            ))
    
    def _verificar_ltv_baixo(self, df: pd.DataFrame):
        """Verifica se existem clientes com LTV muito baixo."""
        if 'LTV_Estimado' not in df.columns:
            return
        
        ltv_medio = df['LTV_Estimado'].mean()
        meta_ltv = self.config.META_LTV_MINIMO
        
        clientes_ltv_baixo = len(df[df['LTV_Estimado'] < meta_ltv])
        
        if ltv_medio < meta_ltv:
            self.alertas.append(Alerta(
                tipo=TipoAlerta.ATENCAO,
                titulo="LTV Médio Abaixo do Esperado",
                mensagem=(
                    f"LTV médio (R$ {ltv_medio:,.2f}) está abaixo da meta "
                    f"(R$ {meta_ltv:,.2f}). {clientes_ltv_baixo} clientes com LTV baixo."
                ),
                metrica_atual=ltv_medio,
                limite=meta_ltv
            ))
    
    def _verificar_trial_expirados(self, df: pd.DataFrame):
        """Verifica quantos clientes estão em trial."""
        trial_count = len(df[df['status'] == 'Trial'])
        total_clientes = len(df)
        
        if total_clientes == 0:
            return
        
        percentual_trial = (trial_count / total_clientes) * 100
        
        # Se mais de 15% estão em trial, pode ser um problema de conversão
        if percentual_trial > 15:
            self.alertas.append(Alerta(
                tipo=TipoAlerta.ATENCAO,
                titulo="Alto Número de Clientes em Trial",
                mensagem=(
                    f"{trial_count} clientes ({percentual_trial:.1f}%) ainda estão "
                    f"em período trial. Considere estratégias de conversão."
                ),
                metrica_atual=trial_count,
                limite=total_clientes * 0.15
            ))
    
    def get_alertas_por_tipo(self, tipo: TipoAlerta) -> List[Alerta]:
        """
        Filtra alertas por tipo.
        
        Args:
            tipo: Tipo de alerta desejado.
            
        Returns:
            Lista de alertas do tipo especificado.
        """
        return [a for a in self.alertas if a.tipo == tipo]
    
    def tem_alertas_criticos(self) -> bool:
        """Verifica se existem alertas críticos."""
        return any(a.tipo == TipoAlerta.CRITICO for a in self.alertas)
