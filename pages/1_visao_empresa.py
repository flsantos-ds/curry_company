# ==============================================================================
# Libraries
# ==============================================================================

import pandas as pd
import re
import plotly.express as px
import folium
from haversine import haversine
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static
import plotly.graph_objects as go
import numpy as np


# ------------------------------------------------------------------------------
# Configuração da Página
# ------------------------------------------------------------------------------

st.set_page_config(page_title = 'Visão Empresa', page_icon = '📊', layout = 'wide')

# ==============================================================================
# Functions
# ==============================================================================

# ------------------------------------------------------------------------------
# Limpandos os dados 
# ------------------------------------------------------------------------------
def clean_code(df):
    
    """ Está função tem a responsabilidade de limpar o dafaframe.
        
        Tipos de limpezas:
        1. Remoção dos dados NaN;
        2. Mudança do tipo da coluna de dados;
        3. Remoção dos espaços das variáveis de texto;
        4. Formatação da coluna de datas;
        5. Limpeza da coluna de tempo (remoção do teto da variável numérica).
        
        Input: Dataframe
        Output: Dataframe
    """
    
    # Eliminar espaços dos textos
    
    df.loc[:, 'ID'] = df.loc[:, 'ID'].str.strip()
    df.loc[:, 'Delivery_person_ID'] = df.loc[:, 'Delivery_person_ID'].str.strip()
    df.loc[:, 'Road_traffic_density'] = df.loc[:, 'Road_traffic_density'].str.strip()
    df.loc[:, 'Type_of_order'] = df.loc[:, 'Type_of_order'].str.strip()
    df.loc[:, 'Type_of_vehicle'] = df.loc[:, 'Type_of_vehicle'].str.strip()
    df.loc[:, 'City'] = df.loc[:, 'City'].str.strip()
    df.loc[:, 'Weatherconditions'] = df.loc[:, 'Weatherconditions'].str.strip()
    df.loc[:, 'multiple_deliveries'] = df.loc[:, 'multiple_deliveries'].str.strip()
    df.loc[:, 'Festival'] = df.loc[:, 'Festival'].str.strip()
    df.loc[:, 'Delivery_person_Age'] = df.loc[:, 'Delivery_person_Age'].str.strip()
    df.loc[:, 'Delivery_person_Ratings'] = df.loc[:, 'Delivery_person_Ratings'].str.strip()

    # Excluindo Linhas com Dados NaN

    linhas_nao_vazias = df['Weatherconditions'] != 'conditions NaN'
    df = df.loc[linhas_nao_vazias,:]
    linhas_nao_vazias = df['multiple_deliveries'] != 'NaN'
    df = df.loc[linhas_nao_vazias, :]
    linhas_nao_vazias = df['Festival'] != 'NaN'
    df = df.loc[linhas_nao_vazias, :]
    linhas_nao_vazias = df['City'] != 'NaN'
    df = df.loc[linhas_nao_vazias, :]
    linhas_nao_vazias = df['Delivery_person_Age'] != 'NaN'
    df = df.loc[linhas_nao_vazias, :]
    linhas_nao_vazias = df['Delivery_person_Ratings'] != 'NaN'
    df = df.loc[linhas_nao_vazias, :]

    # Remover o texto (min) da coluna Time Taken

    df['Time_taken(min)'] = df['Time_taken(min)'].apply(lambda x: x.split('(min) ')[1])
    df['Time_taken(min)'] = df['Time_taken(min)'].astype(int)

    # Conversão de texto / categoria / string para números inteiros e decimais

    df['Delivery_person_Age']= df['Delivery_person_Age'].astype(int)
    df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype(float)

    # Conversão de texto / string para datas

    df['Order_Date'] = pd.to_datetime(df['Order_Date'], format='%d-%m-%Y')
    
    return df

# ------------------------------------------------------------------------------
# Desenhar um gráfico de barra
# ------------------------------------------------------------------------------

def order_metric(df):
    # criar o gráfico
    order_by_date = df.loc[:,['ID', 'Order_Date']].groupby('Order_Date').count().reset_index()
    fig = px.bar(order_by_date, x='Order_Date', y='ID')

    return fig


# ------------------------------------------------------------------------------
# Gerar uma Fig - Agrupamento duas colunas - Pie Plot
# ------------------------------------------------------------------------------

def traffic_order_share(df):

    order_by_road_traffic_density = (df.loc[:, ['ID', 'Road_traffic_density']]
                                     .groupby('Road_traffic_density')
                                     .count()
                                     .reset_index())

    # Criar uma coluna com o valor % para inserir no gráfico
    order_by_road_traffic_density['percent_delivery'] = (order_by_road_traffic_density['ID'] /
                                                         order_by_road_traffic_density['ID']
                                                         .sum())

    fig = px.pie(order_by_road_traffic_density, values='percent_delivery', names='Road_traffic_density')

    return fig


# ------------------------------------------------------------------------------
# Gerar uma Fig - Agrupamento duas colunas - Scatter Plot
# ------------------------------------------------------------------------------

def traffic_order_city(df):

    delivery_by_city_by_road_traffic = (df.loc[:, ['ID', 'City', 'Road_traffic_density']]
                                        .groupby(['City', 'Road_traffic_density'])
                                        .count()
                                        .reset_index())

    fig = px.scatter(delivery_by_city_by_road_traffic, x='City', y='Road_traffic_density', size='ID', color='City')
                
    return fig


# ------------------------------------------------------------------------------
# Gerar uma Fig - Line Plot
# ------------------------------------------------------------------------------

def order_share_by_week(df):

    # contar quantos pedidos foram entregues por semana
    delivery_by_week = (df.loc[:, ['ID', 'week_of_year']]
                        .groupby('week_of_year')
                        .count()
                        .reset_index())

    # contar quanto entregadores únicos fizeram entregas na semanas
    delivery_by_person = (df.loc[:, ['Delivery_person_ID', 'week_of_year']]
                          .groupby('week_of_year')
                          .nunique()
                          .reset_index())

    # unir os dois dataframes
    delivery_by_week_by_person = pd.merge(delivery_by_week, delivery_by_person, how='inner')

    # criar uma coluna com a média de entrega realizado por entregadores únicos por semana
    delivery_by_week_by_person['order_by_delivery'] = (delivery_by_week_by_person['ID'] /
                                                       delivery_by_week_by_person['Delivery_person_ID'])

    # plotar o gráfico de linhas
    fig = px.line(delivery_by_week_by_person, x='week_of_year', y='order_by_delivery')

    return fig

# ------------------------------------------------------------------------------
# Gerar uma Fig - Line Plot
# ------------------------------------------------------------------------------

def order_by_week(df):
    df['week_of_year'] = df['Order_Date'].dt.strftime('%U')

    order_by_week = df.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
    fig = px.line(order_by_week, x='week_of_year', y='ID')
    return fig


# ------------------------------------------------------------------------------
# Gerar um Mapa
# ------------------------------------------------------------------------------

def map_country(df):
    localizacao_media_entregas = (df.loc[:, ['Delivery_location_latitude',
                                             'Delivery_location_longitude',
                                             'City', 'Road_traffic_density']]
                              .groupby(['City', 'Road_traffic_density'])
                              .median()
                              .reset_index())

    map = folium.Map()

    for index, location_info in localizacao_media_entregas.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'],
                       location_info['Delivery_location_longitude']],
                      popup = location_info[['City',
                                             'Road_traffic_density']]).add_to(map)

    folium_static(map, width=1024, height=600)

    return map

# ==============================================================================
# Inicio da Estrutura Lógica
# ==============================================================================

# Import Dataset
# ------------------------------------------------------------------------------

df = pd.read_csv('dataset/train.csv')

# Limpando os dados
# ------------------------------------------------------------------------------

df = clean_code(df)

# ==============================================================================
# Barra Lateral
# ==============================================================================

st.header('Marketplace - Visão Cliente')

# Imagem do Logo que está na Side Bar
# image_path = '/Users/fabioldossantos/Documents/repos/ftc_programacao_pythologo.png'
image = Image.open('logo.png')
st.sidebar.image(image, width=180)

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

# ------------------------------------------------------------------------------
# Criar Filtros

st.sidebar.markdown('### Selecione uma data limite')
data_slider = st.sidebar.slider(
    'Até qual valor?',
    value = pd.datetime(2022,4,13),
    min_value = pd.datetime(2022, 2, 11),
    max_value = pd.datetime(2022, 4, 6),
    format = 'DD-MM-YYYY')

st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito?',
    ['Low', 'Medium', 'High', 'Jam'],
    default = ['Low', 'Medium', 'High', 'Jam'])

# Filtro de Datas
linhas_selecionadas = df['Order_Date'] < data_slider
df = df.loc[linhas_selecionadas, :]

# Filtro de transito
linhas_selecionadas = df['Road_traffic_density'].isin(traffic_options)
df = df.loc[linhas_selecionadas,:]


st.sidebar.markdown("""---""")

st.sidebar.markdown('### Powered by Comunidade DS')

# ==============================================================================
# Layout no Streamlit
# ==============================================================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

# ------------------------------------------------------------------------------
# Criando a primeira Tab
# ------------------------------------------------------------------------------

with tab1:
    # Order Metric

# ------------------------------------------------------------------------------
# Primeiro Container

    with st.container(): # criar um container
        st.markdown('## Order by Day')
        
        fig = order_metric(df)
        
        # usar função para plotar o gráfico
        st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------------------------------------
# Segundo Container - primeiro gráfico

    with st.container(): # criar um container
        col1, col2 = st.columns(2) # criar duas colunas
        
        with col1:
            st.header('Traffic Order Share')
            
            fig = traffic_order_share(df)
            
            st.plotly_chart(fig, use_container_width=True)
            
# ------------------------------------------------------------------------------
# Segundo Container - segundo gráfico

        with col2:
            st.header('Traffic Order City')
            
            fig = traffic_order_city(df)
            
            st.plotly_chart(fig, use_container_with=True)
    
# ------------------------------------------------------------------------------
# Criando a segunda Tab
# ------------------------------------------------------------------------------

with tab2:
    
# ------------------------------------------------------------------------------
# Primeiro Container

    with st.container():
        st.markdown('## Order by Week')
        
        fig = order_by_week(df)
        st.plotly_chart(fig, use_container_with=True)

# ------------------------------------------------------------------------------
# Segundo Container

    with st.container():
        st.markdown('## Order Share by Week')
        
        fig = order_share_by_week(df)
        
        st.plotly_chart(fig, use_container_with=True)
    
# ------------------------------------------------------------------------------
# Criando a teceira Tab
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# Criando o Mapa

with tab3:
    st.markdown('## Country Maps')
    
    map_country(df)
