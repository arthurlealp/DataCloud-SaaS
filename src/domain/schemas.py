"""
Schemas de validação usando Pydantic.
Garante integridade dos dados na entrada do sistema.
"""

from pydantic import BaseModel, validator, Field
from datetime import date
from typing import Optional


class AssinaturaSchema(BaseModel):
    """Schema de validação para assinaturas."""
    assinatura_id: int = Field(..., gt=0, description="ID único da assinatura")
    empresa_id: int = Field(..., gt=0)
    status: str
    data_inicio: date
    preco_mensal: float = Field(..., gt=0, description="Preço deve ser positivo")
    nome_plano: str
    razao_social: str
    cnpj: Optional[str] = None
    proxima_cobranca: Optional[date] = None
    
    @validator('status')
    def status_valido(cls, v):
        """Valida se o status é um dos valores permitidos."""
        validos = ['Ativo', 'Cancelado', 'Trial', 'Inativo']
        if v not in validos:
            raise ValueError(f'Status inválido: {v}. Deve ser um de: {validos}')
        return v
    
    @validator('preco_mensal')
    def preco_positivo(cls, v):
        """Garante que o preço é positivo."""
        if v <= 0:
            raise ValueError('Preço mensal deve ser maior que zero')
        return v
    
    @validator('cnpj')
    def cnpj_formato(cls, v):
        """Valida formato básico do CNPJ."""
        if v and len(v.replace('.', '').replace('/', '').replace('-', '')) != 14:
            raise ValueError('CNPJ deve ter 14 dígitos')
        return v
    
    class Config:
        from_attributes = True


class PlanoSchema(BaseModel):
    """Schema de validação para planos."""
    id: int = Field(..., gt=0)
    nome: str = Field(..., min_length=1, max_length=100)
    preco_mensal: float = Field(..., gt=0)
    limite_usuarios: int = Field(..., ge=1)
    limite_armazenamento: float = Field(..., gt=0)
    
    @validator('nome')
    def nome_nao_vazio(cls, v):
        """Garante que o nome não está vazio."""
        if not v or not v.strip():
            raise ValueError('Nome do plano não pode estar vazio')
        return v.strip()


class EmpresaSchema(BaseModel):
    """Schema de validação para empresas."""
    id: int = Field(..., gt=0)
    razao_social: str = Field(..., min_length=1)
    cnpj: str
    data_criacao: date
    
    @validator('data_criacao')
    def data_nao_futuro(cls, v):
        """Garante que data de criação não é no futuro."""
        if v > date.today():
            raise ValueError('Data de criação não pode ser no futuro')
        return v
