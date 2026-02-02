"""
Modelos de domínio para DataCloud SaaS.
Define as entidades de negócio centrais do sistema.
"""

from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from typing import Optional


class StatusAssinatura(Enum):
    """Estados possíveis de uma assinatura."""
    ATIVO = "Ativo"
    CANCELADO = "Cancelado"
    TRIAL = "Trial"
    INATIVO = "Inativo"


@dataclass
class Plano:
    """Representa um plano de assinatura."""
    id: int
    nome: str
    preco_mensal: float
    limite_usuarios: int
    limite_armazenamento: float  # Em GB
    
    def __post_init__(self):
        if self.preco_mensal <= 0:
            raise ValueError("Preço mensal deve ser positivo")


@dataclass
class Empresa:
    """Representa uma empresa cliente."""
    id: int
    razao_social: str
    cnpj: str
    data_criacao: date
    
    def __post_init__(self):
        if not self.razao_social:
            raise ValueError("Razão social é obrigatória")


@dataclass
class Assinatura:
    """
    Representa um contrato de assinatura.
    
    Contém lógica de negócio para cálculos de KPIs.
    """
    id: int
    empresa_id: int
    plano_id: int
    status: StatusAssinatura
    data_inicio: date
    preco_mensal: float
    data_renovacao: Optional[date] = None
    proxima_cobranca: Optional[date] = None
    
    def calcular_ltv(self, data_referencia: Optional[date] = None) -> float:
        """
        Calcula Lifetime Value (LTV) até a data de referência.
        
        LTV = (Meses como cliente) * Preço mensal
        
        Args:
            data_referencia: Data para cálculo. Se None, usa data atual.
            
        Returns:
            Valor total gasto pelo cliente até a data.
        """
        if data_referencia is None:
            data_referencia = date.today()
        
        dias = (data_referencia - self.data_inicio).days
        meses = max(dias / 30.0, 0)
        ltv = meses * self.preco_mensal
        
        return round(ltv, 2)
    
    def dias_como_cliente(self, data_referencia: Optional[date] = None) -> int:
        """
        Retorna quantos dias o cliente está ativo.
        
        Args:
            data_referencia: Data para cálculo. Se None, usa data atual.
            
        Returns:
            Número de dias desde o início da assinatura.
        """
        if data_referencia is None:
            data_referencia = date.today()
        
        return max((data_referencia - self.data_inicio).days, 0)
    
    def esta_ativa(self) -> bool:
        """Verifica se a assinatura está ativa."""
        return self.status == StatusAssinatura.ATIVO
    
    def esta_em_trial(self) -> bool:
        """Verifica se a assinatura está em período trial."""
        return self.status == StatusAssinatura.TRIAL
    
    def foi_cancelada(self) -> bool:
        """Verifica se a assinatura foi cancelada."""
        return self.status == StatusAssinatura.CANCELADO


@dataclass
class Usuario:
    """Representa um usuário do sistema."""
    id: int
    nome: str
    email: str
    cargo: str
    empresa_id: int
    
    def __post_init__(self):
        if not self.email or "@" not in self.email:
            raise ValueError("Email inválido")
