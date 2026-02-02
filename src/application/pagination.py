"""
Sistema de paginação para dashboard.
Facilita navegação em grandes volumes de dados.
"""

import streamlit as st
import pandas as pd
from math import ceil
from typing import Optional


class Paginator:
    """
    Paginador para DataFrames no Streamlit.
    
    Permite navegar por grandes conjuntos de dados de forma eficiente.
    """
    
    def __init__(
        self,
        df: pd.DataFrame,
        page_size: int = 50,
        key: str = "paginator"
    ):
        """
        Inicializa o paginador.
        
        Args:
            df: DataFrame a paginar.
            page_size: Número de registros por página.
            key: Chave única para o state (permite múltiplos paginadores).
        """
        self.df = df
        self.page_size = page_size
        self.key = key
        self.total_records = len(df)
        self.total_pages = max(ceil(self.total_records / page_size), 1)
        
        # Inicializa state se não existir
        session_key = f"{self.key}_current_page"
        if session_key not in st.session_state:
            st.session_state[session_key] = 1
    
    def get_current_page_number(self) -> int:
        """Retorna número da página atual."""
        return st.session_state.get(f"{self.key}_current_page", 1)
    
    def set_page(self, page_number: int):
        """Define página atual."""
        page_number = max(1, min(page_number, self.total_pages))
        st.session_state[f"{self.key}_current_page"] = page_number
    
    def get_page(self, page_number: Optional[int] = None) -> pd.DataFrame:
        """
        Retorna DataFrame da página especificada.
        
        Args:
            page_number: Número da página (1-indexed). Se None, usa página atual.
            
        Returns:
            DataFrame com registros da página.
        """
        if page_number is None:
            page_number = self.get_current_page_number()
        
        start_idx = (page_number - 1) * self.page_size
        end_idx = start_idx + self.page_size
        
        return self.df.iloc[start_idx:end_idx]
    
    def render_controls(self) -> pd.DataFrame:
        """
        Renderiza controles de paginação no Streamlit.
        
        Returns:
            DataFrame da página atual.
        """
        current_page = self.get_current_page_number()
        
        # Layout dos controles
        col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
        
        with col1:
            if st.button("⏮️ Primeira", key=f"{self.key}_first", use_container_width=True):
                self.set_page(1)
                st.rerun()
        
        with col2:
            if st.button("⬅️ Anterior", key=f"{self.key}_prev", use_container_width=True):
                if current_page > 1:
                    self.set_page(current_page - 1)
                    st.rerun()
        
        with col3:
            st.markdown(
                f"<div style='text-align: center; padding: 8px;'>"
                f"Página <strong>{current_page}</strong> de <strong>{self.total_pages}</strong><br>"
                f"<small>Total: {self.total_records:,} registros</small>"
                f"</div>",
                unsafe_allow_html=True
            )
        
        with col4:
            if st.button("Próxima ➡️", key=f"{self.key}_next", use_container_width=True):
                if current_page < self.total_pages:
                    self.set_page(current_page + 1)
                    st.rerun()
        
        with col5:
            if st.button("Última ⏭️", key=f"{self.key}_last", use_container_width=True):
                self.set_page(self.total_pages)
                st.rerun()
        
        # Seletor de página rápido
        with st.expander("🔍 Ir para página específica"):
            col_a, col_b = st.columns([3, 1])
            with col_a:
                page_input = st.number_input(
                    "Número da página:",
                    min_value=1,
                    max_value=self.total_pages,
                    value=current_page,
                    step=1,
                    key=f"{self.key}_input"
                )
            with col_b:
                if st.button("Ir", key=f"{self.key}_go"):
                    self.set_page(page_input)
                    st.rerun()
        
        return self.get_page(current_page)
    
    def render_simple_controls(self) -> pd.DataFrame:
        """
        Renderiza controles simplificados (apenas anterior/próxima).
        
        Returns:
            DataFrame da página atual.
        """
        current_page = self.get_current_page_number()
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if st.button("⬅️ Anterior", key=f"{self.key}_prev_simple"):
                if current_page > 1:
                    self.set_page(current_page - 1)
                    st.rerun()
        
        with col2:
            st.markdown(
                f"<div style='text-align: center;'>"
                f"Página {current_page} / {self.total_pages} "
                f"({self.total_records:,} registros)"
                f"</div>",
                unsafe_allow_html=True
            )
        
        with col3:
            if st.button("Próxima ➡️", key=f"{self.key}_next_simple"):
                if current_page < self.total_pages:
                    self.set_page(current_page + 1)
                    st.rerun()
        
        return self.get_page(current_page)
    
    def get_page_info(self) -> dict:
        """
        Retorna informações sobre a paginação atual.
        
        Returns:
            Dicionário com informações da página.
        """
        current_page = self.get_current_page_number()
        start_idx = (current_page - 1) * self.page_size + 1
        end_idx = min(start_idx + self.page_size - 1, self.total_records)
        
        return {
            'current_page': current_page,
            'total_pages': self.total_pages,
            'page_size': self.page_size,
            'total_records': self.total_records,
            'start_index': start_idx,
            'end_index': end_idx,
            'showing_count': end_idx - start_idx + 1
        }
