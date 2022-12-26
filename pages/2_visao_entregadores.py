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

st.set_page_config(page_title = 'Visão Entregadores', page_icon = '📈', layout = 'wide')

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
# Top Entregadores
# ------------------------------------------------------------------------------

def top_delivery(df1, top_asc):

    """ Esta função calcula o top entregadores da base de dados, por cidade.

    Parâmetros:
       Input:
           - df: Dataframe com os dados necessários para o cálculo
           - top_asc: Parâmetro que determina a classificação da base de dados.
               - True: Os entregadores mais rápidos.
               - False: Os entregadores mais lentos
       Output:
           - dataframe: um dataframe com a cidade, os IDs dos 10 entregadores e o tempo de entrega.
           
       """
    
    
    selecao = (df.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']]
     .groupby(['City', 'Delivery_person_ID'])
     .min()
     .sort_values(['City', 'Time_taken(min)'], ascending = top_asc)
     .reset_index())

    urban = selecao.loc[selecao['City'] == 'Urban', :].head(10)
    metropolitan = selecao.loc[selecao['City'] == 'Metropolitian', :].head(10)
    semi_urban = selecao.loc[selecao['City'] == 'Semi-Urban', :].head(10)

    dados = pd.concat([urban, metropolitan, semi_urban]).reset_index(drop = True)

    return dados


# ==============================================================================
# Import Dataset
# ==============================================================================

df = pd.read_csv('dataset/train.csv')

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
# image_path = '/Users/fabioldossantos/Documents/repos/ftc_programacao_python/logo.png'
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

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '-', '-'])


with tab1:
    
    with st.container():
        st.title('Overall Metrics')
        col1, col2, col3, col4 = st.columns(4, gap='large')
        
        # Maior idade dos entregadores
        with col1:
            maior_idade = df.loc[:,'Delivery_person_Age'].max()
            col1.metric('Maior idade', maior_idade)
        
        # Menor idade dos entregadores
        with col2:
            menor_idade= df.loc[:,'Delivery_person_Age'].min()
            col2.metric('Menor idade', menor_idade)
        
        # Melhor Condição do Veículo
        with col3:
            melhor_cond = df.loc[:,'Vehicle_condition'].max()
            col3.metric('Melhor Codição Veic',  melhor_cond)
        
        # Pior Condição do Veículo
        with col4:
            pior_cond = df.loc[:,'Vehicle_condition'].min()
            col4.metric('Pior Condição Veic', pior_cond)
            
    with st.container():
        st.markdown("""---""")
        st.title('Avaliações')
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('##### Avalições média por entregador')
            avalicao_media = (df.loc[:, ['Delivery_person_ID', 'Delivery_person_Ratings']]
                    .groupby('Delivery_person_ID')
                    .mean()
                    .reset_index())
            st.dataframe(avalicao_media)
            
        with col2:
            st.markdown('##### Avaliação média por trânsito')
            mean_std_person_ratings = (df.loc[:, ['Delivery_person_Ratings','Road_traffic_density']]
                                .groupby('Road_traffic_density')
                                .agg({'Delivery_person_Ratings': ['mean', 'std']}))

            mean_std_person_ratings.columns = ['mean_ratings', 'std_ratings']

            mean_std_person_ratings.reset_index()
            st.dataframe(mean_std_person_ratings)

            
            st.markdown('##### Avaliação média por clima')
            mean_std_person_ratings = (df.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']]
                               .groupby('Weatherconditions')
                               .agg({'Delivery_person_Ratings': ['mean', 'std']}))

            mean_std_person_ratings.columns = ['mean_Ratings', 'std_Ratings']
            mean_std_person_ratings.reset_index()
            
            st.dataframe(mean_std_person_ratings)
            
    with st.container():
        st.markdown("""---""")
        st.title('Velocidade de entrega')
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Top Entregadores mais rápidos')
            
            dados = top_delivery(df, True)
            
            st.dataframe(dados)
            
        
        with col2:
            st.markdown('##### Top Entregadoers mais lentos')
            
            
            dados = top_delivery(df, False)
            
            st.dataframe(dados)
