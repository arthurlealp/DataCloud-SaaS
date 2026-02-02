"""
Serviço de exportação de relatórios em múltiplos formatos.
Suporta CSV, Excel com formatação e futuramente PDF.
"""

import pandas as pd
from datetime import datetime
from io import BytesIO
import logging
from typing import Optional
from pathlib import Path


class ExportService:
    """
    Serviço para exportação de dados em diferentes formatos.
    
    Gera relatórios formatados prontos para consumo externo.
    """
    
    @staticmethod
    def exportar_csv(
        df: pd.DataFrame,
        nome_arquivo: Optional[str] = None,
        encoding: str = 'utf-8-sig'
    ) -> BytesIO:
        """
        Exporta DataFrame para CSV em memória.
        
        Args:
            df: DataFrame a exportar.
            nome_arquivo: Nome do arquivo (opcional).
            encoding: Encoding do arquivo (utf-8-sig para Excel).
            
        Returns:
            BytesIO contendo o CSV.
        """
        if nome_arquivo is None:
            nome_arquivo = f"relatorio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        buffer = BytesIO()
        df.to_csv(buffer, index=False, encoding=encoding)
        buffer.seek(0)
        
        logging.info(f"CSV gerado: {len(df)} linhas")
        return buffer
    
    @staticmethod
    def exportar_excel(
        df: pd.DataFrame,
        nome_arquivo: Optional[str] = None,
        sheet_name: str = 'Dados',
        incluir_formatacao: bool = True
    ) -> BytesIO:
        """
        Exporta DataFrame para Excel com formatação profissional.
        
        Args:
            df: DataFrame a exportar.
            nome_arquivo: Nome do arquivo (opcional).
            sheet_name: Nome da planilha.
            incluir_formatacao: Se True, aplica formatação automática.
            
        Returns:
            BytesIO contendo o arquivo Excel.
        """
        if nome_arquivo is None:
            nome_arquivo = f"relatorio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        buffer = BytesIO()
        
        try:
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name=sheet_name)
                
                if incluir_formatacao:
                    ExportService._aplicar_formatacao_excel(
                        writer, 
                        sheet_name, 
                        df
                    )
            
            buffer.seek(0)
            logging.info(f"Excel gerado: {len(df)} linhas, {len(df.columns)} colunas")
            return buffer
            
        except Exception as e:
            logging.error(f"Erro ao gerar Excel: {e}")
            raise
    
    @staticmethod
    def _aplicar_formatacao_excel(
        writer,
        sheet_name: str,
        df: pd.DataFrame
    ):
        """
        Aplica formatação profissional ao Excel.
        
        Args:
            writer: ExcelWriter object.
            sheet_name: Nome da planilha.
            df: DataFrame com os dados.
        """
        workbook = writer.book
        worksheet = writer.sheets[sheet_name]
        
        # Formatos
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4472C4',
            'font_color': 'white',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })
        
        money_format = workbook.add_format({
            'num_format': 'R$ #,##0.00',
            'border': 1
        })
        
        date_format = workbook.add_format({
            'num_format': 'dd/mm/yyyy',
            'border': 1
        })
        
        number_format = workbook.add_format({
            'num_format': '#,##0.00',
            'border': 1
        })
        
        text_format = workbook.add_format({
            'border': 1
        })
        
        # Aplica formato no cabeçalho
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
        
        # Aplica largura automática e formatos por coluna
        for idx, col in enumerate(df.columns):
            # Calcula largura ideal
            max_len = max(
                df[col].astype(str).map(len).max(),
                len(col)
            ) + 2
            worksheet.set_column(idx, idx, min(max_len, 50))  # Máximo 50
            
            # Detecta tipo e aplica formato
            col_lower = col.lower()
            
            if any(keyword in col_lower for keyword in ['preco', 'valor', 'ltv', 'receita', 'mrr']):
                # Formato de moeda
                for row_num in range(1, len(df) + 1):
                    worksheet.write(row_num, idx, df.iloc[row_num - 1, idx], money_format)
            
            elif 'data' in col_lower:
                # Formato de data
                for row_num in range(1, len(df) + 1):
                    worksheet.write(row_num, idx, df.iloc[row_num - 1, idx], date_format)
            
            elif df[col].dtype in ['float64', 'int64']:
                # Formato numérico
                for row_num in range(1, len(df) + 1):
                    worksheet.write(row_num, idx, df.iloc[row_num - 1, idx], number_format)
        
        # Adiciona filtros
        worksheet.autofilter(0, 0, len(df), len(df.columns) - 1)
        
        # Congela primeira linha
        worksheet.freeze_panes(1, 0)
    
    @staticmethod
    def salvar_em_arquivo(
        buffer: BytesIO,
        caminho: str
    ) -> Path:
        """
        Salva buffer em arquivo no disco.
        
        Args:
            buffer: BytesIO com conteúdo.
            caminho: Caminho onde salvar.
            
        Returns:
            Path do arquivo salvo.
        """
        caminho_path = Path(caminho)
        caminho_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(caminho_path, 'wb') as f:
            f.write(buffer.getvalue())
        
        logging.info(f"Arquivo salvo em: {caminho_path}")
        return caminho_path
    
    @staticmethod
    def gerar_relatorio_resumo(df: pd.DataFrame) -> pd.DataFrame:
        """
        Gera DataFrame resumido com estatísticas.
        
        Args:
            df: DataFrame completo.
            
        Returns:
            DataFrame com resumo estatístico.
        """
        if df.empty:
            return pd.DataFrame()
        
        resumo = {
            'Total de Registros': [len(df)],
            'Receita Total (MRR)': [df[df['status'] != 'Cancelado']['preco_mensal'].sum()],
            'Ticket Médio': [df['preco_mensal'].mean()],
            'Clientes Ativos': [len(df[df['status'] == 'Ativo'])],
            'Clientes Cancelados': [len(df[df['status'] == 'Cancelado'])],
            'Taxa de Churn': [len(df[df['status'] == 'Cancelado']) / len(df) * 100],
        }
        
        if 'LTV_Estimado' in df.columns:
            resumo['LTV Médio'] = [df['LTV_Estimado'].mean()]
        
        return pd.DataFrame(resumo)
