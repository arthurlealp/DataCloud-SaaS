"""
Dashboard Streamlit do DataCloud SaaS.
Versão refatorada com nova arquitetura.
"""

import streamlit as st
import pandas as pd
from datetime import datetime

# Importações da nova arquitetura
from config.settings import settings
from config.logging_config import setup_logging
from src.application.etl_service import SaasETLService
from src.application.kpi_calculator import KPICalculator
from src.application.alerts import AlertaService
from src.application.export_service import ExportService
from src.application.pagination import Paginator
from src.presentation.auth import AuthService

# Configura logging
setup_logging(log_level=settings.LOG_LEVEL, log_dir=settings.LOG_DIR)

# === CONFIGURAÇÃO DA PÁGINA ===
st.set_page_config(
    page_title=settings.DASHBOARD_TITLE,
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === CSS PERSONALIZADO ===
st.markdown("""
    <style>
    .block-container {padding-top: 1rem; padding-bottom: 0rem;}
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)


# === FUNÇÃO DE CACHE PARA DADOS ===
@st.cache_data(ttl=settings.CACHE_TTL)
def carregar_dados():
    """Carrega dados do banco com cache de 5 minutos."""
    etl = SaasETLService()
    dados_brutos = etl.extrair(validar=False)
    dados_tratados = etl.transformar(dados_brutos)
    
    return {
        'dados': dados_tratados,
        'ultima_atualizacao': datetime.now(),
        'total_registros': len(dados_tratados)
    }


# === AUTENTICAÇÃO (SE CONFIGURADA) ===
if settings.REQUIRE_AUTH:
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        AuthService.exibir_login()
        st.stop()


# === INÍCIO DO DASHBOARD ===
st.title(f"🚀 {settings.DASHBOARD_TITLE}")
st.markdown("Monitoramento financeiro e operacional em tempo real")

# Carrega dados
try:
    resultado = carregar_dados()
    df = resultado['dados']
    
    # Verifica se DataFrame está vazio
    if df.empty:
        st.warning("⚠️ Banco de dados vazio")
        st.info("""
        � **Para popular o banco de dados com dados de exemplo:**
        
        Execute no terminal:
        ```bash
        python utils/seed.py
        ```
        
        Depois, volte aqui e clique em **"� Atualizar Dados"**.
        """)
        st.stop()
    
    # Informações de atualização
    col_info1, col_info2 = st.columns([3, 1])
    with col_info1:
        st.caption(f"📊 Última atualização: {resultado['ultima_atualizacao'].strftime('%d/%m/%Y %H:%M:%S')}")
    with col_info2:
        if st.button("🔄 Atualizar Dados", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
except Exception as e:
    st.error(f"❌ Erro ao carregar dados: {e}")
    st.info("💡 Verifique se o banco de dados existe e foi inicializado com `python utils/seed.py`")
    st.stop()


# === SIDEBAR - FILTROS E CONTROLES ===
with st.sidebar:
    st.header("🎛️ Painel de Controle")
    
    # Filtro de Planos
    todos_planos = df["nome_plano"].unique()
    filtro_plano = st.multiselect(
        "Filtrar por Plano:",
        options=todos_planos,
        default=todos_planos,
        key="filtro_plano"
    )
    
    # Filtro de Status
    todos_status = df["status"].unique()
    filtro_status = st.multiselect(
        "Filtrar por Status:",
        options=todos_status,
        default=todos_status,
        key="filtro_status"
    )
    
    st.divider()
    
    # Exportação
    st.subheader("📥 Exportar Dados")
    df_para_exportar = df[(df["nome_plano"].isin(filtro_plano)) & (df["status"].isin(filtro_status))]
    
    col1, col2 = st.columns(2)
    with col1:
        csv_buffer = ExportService.exportar_csv(df_para_exportar)
        st.download_button(
            label="💾 CSV",
            data=csv_buffer,
            file_name=f"relatorio_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        excel_buffer = ExportService.exportar_excel(df_para_exportar)
        st.download_button(
            label="📊 Excel",
            data=excel_buffer,
            file_name=f"relatorio_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    # === SOBRE O DESENVOLVEDOR ===
    st.divider()
    st.markdown("### 👨‍💻 Sobre o Desenvolvedor")
    
    col_foto, col_info = st.columns([1, 3])
    with col_foto:
        st.image("https://github.com/arthurlealp.png", width=60)
    with col_info:
        st.markdown("**Arthur Leal Pacheco**")
        st.caption("Data Engineer")
    
    st.markdown("""
    [![LinkedIn](https://img.shields.io/badge/-LinkedIn-0077B5?style=flat&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/arthur-leal-pacheco-b95058353/)
    [![GitHub](https://img.shields.io/badge/-GitHub-181717?style=flat&logo=github&logoColor=white)](https://github.com/arthurlealp)
    """)
    
    st.caption("💡 Projeto open-source desenvolvido para demonstrar Clean Architecture e boas práticas em Python + Streamlit")
    
    # Se autenticação estiver ativa, mostra info do usuário
    if settings.REQUIRE_AUTH:
        AuthService.render_user_info()


# === APLICAÇÃO DOS FILTROS ===
df_filtrado = df[
    (df["nome_plano"].isin(filtro_plano)) & 
    (df["status"].isin(filtro_status))
]

if df_filtrado.empty:
    st.warning("⚠️ Nenhum dado encontrado com os filtros selecionados.")
    st.stop()


# === CÁLCULO DE KPIS ===
metricas = KPICalculator.calcular_metricas(df_filtrado)

# === ALERTAS ===
alert_service = AlertaService(settings)
alertas = alert_service.verificar_alertas(df_filtrado)

if alertas:
    st.subheader("🔔 Alertas do Sistema")
    for alerta in alertas:
        if alerta.tipo.value == "🚨":
            st.error(f"{alerta.tipo.value} **{alerta.titulo}**: {alerta.mensagem}")
        elif alerta.tipo.value == "⚠️":
            st.warning(f"{alerta.tipo.value} **{alerta.titulo}**: {alerta.mensagem}")
        else:
            st.info(f"{alerta.tipo.value} **{alerta.titulo}**: {alerta.mensagem}")
    st.divider()


# === MÉTRICAS PRINCIPAIS ===
st.subheader("📈 Indicadores Chave (KPIs)")

col1, col2, col3, col4 = st.columns(4)

# Calcula delta vs meta
delta_receita = metricas.mrr - settings.META_RECEITA_MENSAL

col1.metric(
    "MRR (Receita Mensal)", 
    f"R$ {metricas.mrr:,.2f}",
    delta=f"{delta_receita:,.2f} vs Meta",
    delta_color="normal"
)

col2.metric(
    "Clientes Totais", 
    metricas.total_clientes,
    delta=f"{metricas.clientes_ativos} ativos"
)

col3.metric(
    "LTV Médio", 
    f"R$ {metricas.ltv_medio:,.2f}",
    help="Lifetime Value médio por cliente"
)

col4.metric(
    "Churn Rate", 
    f"{metricas.taxa_churn:.1%}",
    delta=f"-{metricas.churn_count} clientes",
    delta_color="inverse"
)

st.divider()

# === ABAS DE NAVEGAÇÃO ===
tab1, tab2, tab3 = st.tabs(["📊 Visão Gráfica", "📋 Detalhes dos Dados", "📈 Análise Temporal"])

with tab1:
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("💰 Receita por Plano")
        receita_plano = KPICalculator.calcular_receita_por_plano(df_filtrado)
        if receita_plano:
            # Converte dict para pandas Series
            receita_series = pd.Series(receita_plano)
            st.bar_chart(receita_series, color="#29b5e8")
        else:
            st.info("Sem dados para exibir")
    
    with c2:
        st.subheader("📊 Distribuição de Status")
        df_status = df_filtrado["status"].value_counts()
        st.bar_chart(df_status, color="#e85d75")

with tab2:
    st.subheader("📋 Base de Clientes Detalhada")
    
    # Paginação
    paginator = Paginator(df_filtrado, page_size=settings.PAGE_SIZE, key="main_table")
    df_pagina = paginator.render_controls()
    
    # Exibe tabela
    st.dataframe(
        df_pagina[[
            "assinatura_id", 
            "razao_social", 
            "nome_plano", 
            "status", 
            "data_inicio", 
            "preco_mensal",
            "LTV_Estimado"
        ]],
        use_container_width=True,
        hide_index=True,
        column_config={
            "assinatura_id": "ID",
            "razao_social": "Empresa",
            "nome_plano": "Plano",
            "status": "Status",
            "data_inicio": st.column_config.DateColumn("Data Início", format="DD/MM/YYYY"),
            "preco_mensal": st.column_config.NumberColumn("Preço Mensal", format="R$ %.2f"),
            "LTV_Estimado": st.column_config.NumberColumn("LTV", format="R$ %.2f")
        }
    )

with tab3:
    st.subheader("📈 Evolução de Novos Clientes (Timeline)")
    
    # Cria coluna de mês/ano
    df_timeline = df_filtrado.copy()
    df_timeline['mes_ano'] = df_timeline['data_inicio'].dt.to_period('M').astype(str)
    
    # Agrupa por mês
    novos_por_mes = df_timeline.groupby('mes_ano')['assinatura_id'].count()
    
    if not novos_por_mes.empty:
        st.line_chart(novos_por_mes, color="#4CAF50")
    else:
        st.info("Sem dados suficientes para análise temporal")
    
    # Estatísticas adicionais
    st.subheader("📊 Estatísticas Resumidas")
    resumo = ExportService.gerar_relatorio_resumo(df_filtrado)
    st.dataframe(resumo, use_container_width=True, hide_index=True)

# === RODAPÉ ===
st.divider()
st.caption(f"DataCloud SaaS Analytics © 2026 | Total de {len(df_filtrado):,} registros exibidos | Ambiente: {settings.ENV}")