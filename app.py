import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
import folium
from streamlit_folium import folium_static
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable

# Configuração da página Streamlit
st.set_page_config(layout="wide")

# Paleta de cores personalizada
color_palette = ['#EDAFB8', '#F7E1D7', '#DEDBD2', '#d62728', '#B0C4B1', '#4A5759', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']

# Carregamento e pré-processamento de dados
@st.cache_data
def carregar_e_preprocessar_dados():
    df = pd.read_csv('Amazon Sale Report.csv')
    df.rename(columns={'Sales Channel ': 'Sales Channel'}, inplace=True)
    df['Courier Status'].fillna('Unknown', inplace=True)
    df['currency'].fillna('Unknown', inplace=True)
    df['Amount'] = df.groupby('Category')['Amount'].transform(lambda x: x.fillna(x.mean()))
    df['promotion-ids'] = df['promotion-ids'].notna()
    df.drop(columns=['fulfilled-by', 'Unnamed: 22', 'SKU'], inplace=True)
    df['Date'] = pd.to_datetime(df['Date'])
    return df

df = carregar_e_preprocessar_dados()

# Funções utilitárias
def criar_grafico_barras(data, x, y, titulo, xlabel, ylabel, rotation=45):
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=data, x=x, y=y, palette=color_palette, ax=ax)
    ax.set_title(titulo, fontsize=16)
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    plt.xticks(rotation=rotation)
    plt.tight_layout()
    return fig

@st.cache_data
def obter_coordenadas(cidade):
    geolocator = Nominatim(user_agent="meu_agente")
    try:
        location = geolocator.geocode(cidade)
        if location:
            return (location.latitude, location.longitude)
    except (GeocoderTimedOut, GeocoderUnavailable):
        pass
    return None

# Dashboard principal
st.title("Dashboard de Vendas da Amazon")

# Vendas por Mês
st.header("Análise de Vendas Mensais")
vendas_por_mes = df.groupby(df['Date'].dt.strftime('%B'))['Amount'].sum().reset_index()
vendas_por_mes['Date'] = pd.to_datetime(vendas_por_mes['Date'], format='%B')
vendas_por_mes = vendas_por_mes.sort_values('Date')
vendas_por_mes.columns = ['Mês', 'Total de Vendas']

col1, col2 = st.columns(2)

with col1:
    fig_month = criar_grafico_barras(vendas_por_mes, 'Mês', 'Total de Vendas',
                                     'Total de Vendas por Mês', 'Mês', 'Total de Vendas (R$)')
    st.pyplot(fig_month)

with col2:
    st.subheader("Dados de Vendas Mensais")
    st.dataframe(vendas_por_mes.style.format({'Total de Vendas': 'R${:,.2f}'}))

# Análise por Categoria
st.header("Análise de Categoria de Produtos")
vendas_categoria = df.groupby('Category').agg({'Qty': 'sum', 'Amount': 'sum'}).reset_index()

col1, col2 = st.columns(2)

with col1:
    fig_qty = criar_grafico_barras(vendas_categoria, 'Qty', 'Category',
                                   'Quantidade Vendida por Categoria', 'Quantidade', 'Categoria')
    st.pyplot(fig_qty)

with col2:
    fig_amount = criar_grafico_barras(vendas_categoria, 'Amount', 'Category',
                                      'Total de Vendas por Categoria', 'Total de Vendas (R$)', 'Categoria')
    st.pyplot(fig_amount)

st.subheader("Dados de Vendas por Categoria")
st.dataframe(vendas_categoria.style.format({'Amount': 'R${:,.2f}'}))

# Desempenho do Correio
st.header("Análise de Desempenho do Correio")
status_correio = df['Courier Status'].value_counts().reset_index()
status_correio.columns = ['Status do Correio', 'Frequência']

fig_courier = criar_grafico_barras(status_correio, 'Frequência', 'Status do Correio',
                                   'Desempenho de Entrega por Status do Correio', 'Frequência', 'Status do Correio')
st.pyplot(fig_courier)

st.subheader("Dados de Status do Correio")
st.dataframe(status_correio)

# Vendas por Localização
st.header("Principais Locais de Venda")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Top 10 Cidades por Vendas")
    vendas_por_cidade = df.groupby('ship-city')['Amount'].sum().sort_values(ascending=False).head(10)
    fig_cities = criar_grafico_barras(vendas_por_cidade.reset_index(), 'Amount', 'ship-city',
                                      'Top 10 Cidades por Vendas', 'Total de Vendas (R$)', 'Cidade')
    st.pyplot(fig_cities)

with col2:
    st.subheader("Top 10 Estados por Vendas")
    vendas_por_estado = df.groupby('ship-state')['Amount'].sum().sort_values(ascending=False).head(10)
    fig_states = criar_grafico_barras(vendas_por_estado.reset_index(), 'Amount', 'ship-state',
                                      'Top 10 Estados por Vendas', 'Total de Vendas (R$)', 'Estado')
    st.pyplot(fig_states)

# Mapa de Calor de Categorias de Produtos e Estados
st.header("Relação entre Categorias de Produtos e Estados")
categoria_regiao = df.groupby(['Category', 'ship-state'])['Amount'].sum().unstack()
fig, ax = plt.subplots(figsize=(12, 8))
sns.heatmap(categoria_regiao, cmap='YlOrRd', annot=False, ax=ax)
ax.set_title('Relação entre Categorias de Produtos e Estados', fontsize=16)
ax.set_xlabel('Estados', fontsize=12)
ax.set_ylabel('Categorias', fontsize=12)
plt.tight_layout()
st.pyplot(fig)

# Impacto das Promoções
st.header("Impacto das Promoções nas Vendas")
impacto_promo = df.groupby('promotion-ids')['Amount'].sum()
fig, ax = plt.subplots(figsize=(10, 6))
impacto_promo.plot(kind='pie', ax=ax, autopct='%1.1f%%', startangle=90, colors=color_palette[:2])
ax.set_title('Impacto das Promoções nas Vendas', fontsize=16)
ax.set_ylabel('')  # Remove o rótulo do eixo y
plt.axis('equal')
st.pyplot(fig)

# Vendas por Data
st.header("Análise de Vendas Diárias")
data_min = df['Date'].min().date()
data_max = df['Date'].max().date()
data_selecionada = st.date_input(
    "Selecione uma data",
    min_value=data_min,
    max_value=data_max,
    value=data_min
)

dados_selecionados = df[df['Date'].dt.date == data_selecionada]
qtd_vendida = dados_selecionados['Qty'].sum()
total_vendas = dados_selecionados['Amount'].sum()

col1, col2 = st.columns(2)
with col1:
    st.metric(label=f"Produtos Vendidos em {data_selecionada.strftime('%d/%m/%Y')}", value=qtd_vendida)
with col2:
    st.metric(label=f"Total de Vendas em {data_selecionada.strftime('%d/%m/%Y')}", value=f"R${total_vendas:,.2f}")

# Mapa de Vendas
st.subheader(f"Mapa de Vendas para {data_selecionada.strftime('%d/%m/%Y')} (Top 150 Cidades)")
m = folium.Map(location=[0, 0], zoom_start=2, tiles="cartodbpositron")

top_cidades = dados_selecionados['ship-city'].value_counts().nlargest(150).index

for cidade in top_cidades:
    coordenadas = obter_coordenadas(cidade)
    if coordenadas:
        folium.Marker(
            location=coordenadas,
            popup=f"Cidade: {cidade}"
        ).add_to(m)

folium_static(m)