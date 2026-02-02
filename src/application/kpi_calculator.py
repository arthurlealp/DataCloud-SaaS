"""
Serviço para cálculo de KPIs e métricas de negócio.
Centraliza toda a lógica de indicadores financeiros.
"""

import pandas as pd
import logging
from typing import Dict, Optional
from datetime import date
from dataclasses import dataclass


@dataclass
class KPIMetrics:
    """Estrutura para armazenar métricas calculadas."""
    mrr: float  # Monthly Recurring Revenue
    arr: float  # Annual Recurring Revenue
    total_clientes: int
    ltv_medio: float
    churn_count: int
    taxa_churn: float
    clientes_trial: int
    clientes_ativos: int
    clientes_cancelados: int
    ticket_medio: float


class KPICalculator:
    """
    Calculadora de KPIs para análise de negócio SaaS.
    
    Calcula métricas essenciais como MRR, LTV, Churn, etc.
    """
    
    @staticmethod
    def calcular_metricas(df: pd.DataFrame) -> KPIMetrics:
        """
        Calcula todas as métricas de KPI de uma vez.
        
        Args:
            df: DataFrame com dados de assinaturas.
            
        Returns:
            Objeto KPIMetrics com todas as métricas calculadas.
        """
        if df.empty:
            logging.warning("DataFrame vazio, retornando métricas zeradas")
            return KPIMetrics(
                mrr=0.0,
                arr=0.0,
                total_clientes=0,
                ltv_medio=0.0,
                churn_count=0,
                taxa_churn=0.0,
                clientes_trial=0,
                clientes_ativos=0,
                clientes_cancelados=0,
                ticket_medio=0.0
            )
        
        # Garante que coluna de LTV existe
        if 'LTV_Estimado' not in df.columns:
            df = KPICalculator.calcular_ltv(df)
        
        # Cálculos
        mrr = df[df['status'] != 'Cancelado']['preco_mensal'].sum()
        arr = mrr * 12
        total_clientes = len(df)
        ltv_medio = df['LTV_Estimado'].mean() if not df['LTV_Estimado'].empty else 0.0
        
        churn_count = len(df[df['status'] == 'Cancelado'])
        taxa_churn = (churn_count / total_clientes) if total_clientes > 0 else 0.0
        
        clientes_trial = len(df[df['status'] == 'Trial'])
        clientes_ativos = len(df[df['status'] == 'Ativo'])
        clientes_cancelados = churn_count
        
        ticket_medio = df['preco_mensal'].mean()
        
        metricas = KPIMetrics(
            mrr=round(mrr, 2),
            arr=round(arr, 2),
            total_clientes=total_clientes,
            ltv_medio=round(ltv_medio, 2),
            churn_count=churn_count,
            taxa_churn=round(taxa_churn, 4),
            clientes_trial=clientes_trial,
            clientes_ativos=clientes_ativos,
            clientes_cancelados=clientes_cancelados,
            ticket_medio=round(ticket_medio, 2)
        )
        
        logging.info(f"KPIs calculados: MRR={metricas.mrr}, Churn={metricas.taxa_churn:.2%}")
        return metricas
    
    @staticmethod
    def calcular_ltv(df: pd.DataFrame, data_referencia: Optional[date] = None) -> pd.DataFrame:
        """
        Adiciona coluna de LTV (Lifetime Value) ao DataFrame.
        
        Args:
            df: DataFrame com dados de assinaturas.
            data_referencia: Data para cálculo. Se None, usa hoje.
            
        Returns:
            DataFrame com coluna 'LTV_Estimado' adicionada.
        """
        if df.empty:
            return df
        
        df = df.copy()
        
        # Garante que data_inicio é datetime
        if 'data_inicio' in df.columns:
            df['data_inicio'] = pd.to_datetime(df['data_inicio'])
        
        # Calcula dias de cliente
        if data_referencia is None:
            data_referencia = pd.Timestamp.now()
        
        df['dias_de_cliente'] = (data_referencia - df['data_inicio']).dt.days
        df['dias_de_cliente'] = df['dias_de_cliente'].clip(lower=0)  # Não permite negativos
        
        # Calcula LTV: (dias / 30) * preço_mensal
        df['LTV_Estimado'] = (df['dias_de_cliente'] / 30.0) * df['preco_mensal']
        df['LTV_Estimado'] = df['LTV_Estimado'].round(2)
        
        logging.debug(f"LTV calculado para {len(df)} registros")
        return df
    
    @staticmethod
    def calcular_cohort(
        df: pd.DataFrame, 
        freq: str = 'M'
    ) -> pd.DataFrame:
        """
        Análise de cohort por período.
        
        Args:
            df: DataFrame com assinaturas.
            freq: Frequência ('M' para mensal, 'Q' para trimestral).
            
        Returns:
            DataFrame com análise de cohort.
        """
        if df.empty:
            return pd.DataFrame()
        
        df = df.copy()
        df['data_inicio'] = pd.to_datetime(df['data_inicio'])
        df['cohort'] = df['data_inicio'].dt.to_period(freq)
        
        cohort_analysis = df.groupby('cohort').agg({
            'assinatura_id': 'count',
            'preco_mensal': 'sum',
            'LTV_Estimado': 'mean' if 'LTV_Estimado' in df.columns else lambda x: 0
        }).rename(columns={
            'assinatura_id': 'novos_clientes',
            'preco_mensal': 'receita_cohort',
            'LTV_Estimado': 'ltv_medio_cohort'
        })
        
        return cohort_analysis
    
    @staticmethod
    def calcular_receita_por_plano(df: pd.DataFrame) -> Dict[str, float]:
        """
        Calcula receita por plano.
        
        Args:
            df: DataFrame com assinaturas.
            
        Returns:
            Dicionário {nome_plano: receita_total}.
        """
        if df.empty:
            return {}
        
        # Exclui cancelados do cálculo
        df_ativos = df[df['status'] != 'Cancelado']
        
        receita_por_plano = df_ativos.groupby('nome_plano')['preco_mensal'].sum()
        return receita_por_plano.to_dict()
    
    @staticmethod
    def calcular_crescimento_mrr(
        df_atual: pd.DataFrame,
        df_anterior: pd.DataFrame
    ) -> float:
        """
        Calcula crescimento percentual de MRR.
        
        Args:
            df_atual: DataFrame do período atual.
            df_anterior: DataFrame do período anterior.
            
        Returns:
            Percentual de crescimento (0.15 = 15% de crescimento).
        """
        mrr_atual = df_atual[df_atual['status'] != 'Cancelado']['preco_mensal'].sum()
        mrr_anterior = df_anterior[df_anterior['status'] != 'Cancelado']['preco_mensal'].sum()
        
        if mrr_anterior == 0:
            return 0.0
        
        crescimento = (mrr_atual - mrr_anterior) / mrr_anterior
        return round(crescimento, 4)
