import streamlit as st
import pandas as pd
import plotly.express as px
import requests 
import openpyxl


# Configuração da página

st.logo("LOGO.png", size="large", icon_image="Assinatura visual 1B.png")
st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded"
)


# --- Configuração da página ---
st.set_page_config(layout="wide", initial_sidebar_state="expanded")

df = pd.read_excel("dados.xlsx")

st.title('FP&A - FMCE')

# --- Preparação dos dados ---
df['Dt.Competência'] = pd.to_datetime(df['Dt.Competência'], format='%d/%m/%y')

# --- Barra lateral com filtro de datas e estilo ---
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        background-color: #002d70;
        color: white;
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    /* Fonte da data nos inputs */
    [data-testid="stSidebar"] input {
        color: #FFD700 !important;   /* cor da fonte da data (exemplo: dourado) */
    }
    /* Bordas suaves para os gráficos */
    .grafico-box {
        border: 1px solid #ccc;
        border-radius: 8px;
        padding: 10px;
        margin-bottom: 20px;
        background-color: #f9f9f9;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.sidebar.header("Filtros de Data")
data_inicio = st.sidebar.date_input("Data inicial", df['Dt.Competência'].min())
data_fim = st.sidebar.date_input("Data final", df['Dt.Competência'].max())

df_filtrado = df[(df['Dt.Competência'] >= pd.to_datetime(data_inicio)) &
                 (df['Dt.Competência'] <= pd.to_datetime(data_fim))]

# --- Receitas ---
df_receitas = df_filtrado[df_filtrado['Cod.1'] == 3.1]

# --- Custos e Despesas ---
df_CeD = df_filtrado[df_filtrado['Cod.1'].isin([4.1, 4.2, 4.3])]
mapa_cod = {4.1: "Custos", 4.2: "Despesas", 4.3: "Outras Despesas"}
df_CeD['Categoria'] = df_CeD['Cod.1'].map(mapa_cod)

# --- Receita Mensal ---
receita_mensal = (
    df_receitas
    .set_index('Dt.Competência')
    .groupby(pd.Grouper(freq='M'))['Valor Título']
    .sum()
    .reset_index()
)
receita_mensal['Ano'] = receita_mensal['Dt.Competência'].dt.year
receita_mensal['Mes'] = receita_mensal['Dt.Competência'].dt.month_name()

# --- Receita Mensal Desagregada ---
receita_mensal_desagregada = (
    df_receitas
    .set_index('Dt.Competência')
    .groupby([pd.Grouper(freq='M'), 'Conta Fina'])['Valor Título']
    .sum()
    .reset_index()
)

# --- Custos e Despesas Mensais ---
Despesas_Custos = (
    df_CeD
    .set_index('Dt.Competência')
    .groupby([pd.Grouper(freq='M'), 'Categoria'])['Valor Título']
    .sum()
    .reset_index()
)

# --- Gráficos ---
fig_mensal_receitas = px.line(
    receita_mensal,
    x='Mes',
    y='Valor Título',
    markers=True,
    range_y=(0, receita_mensal['Valor Título'].max()),
    color='Ano',
    line_dash='Ano',
    title="Receita Mensal"
)

fig_mensal_receitas_desagregada = px.line(
    receita_mensal_desagregada,
    x='Dt.Competência',
    y='Valor Título',
    range_y=(0, receita_mensal_desagregada['Valor Título'].max()),
    color='Conta Fina',
    line_dash='Conta Fina',
    title="Receita Mensal por Subcategoria"
)

fig_CeD = px.line(
    Despesas_Custos,
    x='Dt.Competência',
    y='Valor Título',
    range_y=(0, Despesas_Custos['Valor Título'].max()),
    color='Categoria',
    line_dash='Categoria',
    title="Custos e Despesas"
)

# --- Layout em colunas com bordas ---
col1, col2 = st.columns(2)
with col1:
    st.markdown('<div class="grafico-box">', unsafe_allow_html=True)
    st.plotly_chart(fig_mensal_receitas, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="grafico-box">', unsafe_allow_html=True)
    st.plotly_chart(fig_mensal_receitas_desagregada, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

col3, col4 = st.columns(2)
with col3:
    st.markdown('<div class="grafico-box">', unsafe_allow_html=True)
    st.plotly_chart(fig_CeD, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- Gráfico de Pizza (2025) ---
df_2025 = df_receitas[df_receitas['Dt.Competência'].dt.year == 2025]
despesas_2025 = (
    df_2025
    .groupby('Conta Fina')['Valor Título']
    .sum()
    .reset_index()
)

fig_pizza_despesas = px.pie(
    despesas_2025,
    names='Conta Fina',
    values='Valor Título',
    title='Distribuição das Despesas em 2025',
    hole=0.3
)

# Remover rótulos internos
fig_pizza_despesas.update_traces(textinfo='none')

# Ajuste da legenda para não cortar
fig_pizza_despesas.update_layout(
    legend=dict(
        orientation="v",
        yanchor="top",
        y=1,
        xanchor="left",
        x=1.05
    ),
    margin=dict(l=40, r=150, t=40, b=40)
)

with col4:
    st.markdown('<div class="grafico-box">', unsafe_allow_html=True)
    st.plotly_chart(fig_pizza_despesas, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)




































