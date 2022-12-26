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

st.set_page_config(page_title = 'Visão Restaurantes', page_icon = '🥗', layout = 'wide')

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
# Distância entre pontos - Haversine
# ------------------------------------------------------------------------------

def distance(df, avg_by_city=''):
    

    """ Esta função calcula o distância média e o desvio padrão, entre dois pontos (resturantes e local da entrega).
    Para a realização desse cálculo é utilizado a função de Haversine.

    Parâmetros:
       Input:
           - df: Dataframe com os dados necessários para o cálculo
               - Latitude e Longitude do restaurante
               - Latitude e Longitude do local da entrega:
           - avg_by_city:
               - True: quando o resultado esperado deve ser feita a agregação por cidade
               - False: quando o resultao esperado não deve ser feito a agregação por cidade
           - operacao: Tipo de operação que precisa ser calculado, sendo elas:
               - 'avg_time': Calcula o tempo médio
               - 'std_time': Calcula o desvio padrão do tempo
       Output:
           - Sem a agregação por cidade:
               - df_aux: dataframe com a respectiva agregação, com as métricas média e desvio padrão da distância entre os dois pontos.
           - Com a agregação por cidade:
               - fig: objeto em um gráfico de pizza
           
           
    """

    
    if avg_by_city == False:
        
        df['distance'] = (
                df.loc[:, ['Restaurant_latitude',
                           'Restaurant_longitude',
                           'Delivery_location_latitude',
                           'Delivery_location_longitude']]
                    .apply(lambda x :
                           haversine(
                               (x['Restaurant_latitude'], x['Restaurant_longitude']),
                               (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1))

        avg_distance = np.round(df['distance'].mean(), 2)

        return avg_distance
    
    else:

        df['distance'] = (
            df.loc[:, ['Restaurant_latitude',
                       'Restaurant_longitude',
                       'Delivery_location_latitude',
                       'Delivery_location_longitude']]
                .apply(lambda x :
                       haversine(
                           (x['Restaurant_latitude'], x['Restaurant_longitude']),
                           (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1))

        avg_distance = df.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()

        # avg_distance
        # pull is given as a fraction of the pie radius
        fig = go.Figure( data = [go.Pie(labels = avg_distance['City'], values = avg_distance['distance'], pull = [0.1, 0, 0])])
        
        return fig


# ------------------------------------------------------------------------------
# Calcular o a média ou o desvio padrão da entrega 
# ------------------------------------------------------------------------------

def avg_st_time_delivery(df, operacao, festival=''):

    """ Esta função calcula o tempo médio e o desvio padrão de entrega.

    Parâmetros:
       Input:
           - df: Dataframe com os dados necessários para o cálculo
           - operacao: Tipo de operação que precisa ser calculado, sendo elas:
               - 'avg_time': Calcula o tempo médio
               - 'std_time': Calcula o desvio padrão do tempo
           - festival:
               - 'Yes': Considerar as entregas de período que era durante o festival.
               - 'No': Considerar as entregas de período que não foram de festival
       Output:
           - df: Dataframe com 2 colunas e 1 linha.

    """

    festival_time_taken = (df.loc[:, ['Time_taken(min)', 'Festival']]
                                  .groupby('Festival')
                                  .agg({'Time_taken(min)': ['mean', 'std']}))

    festival_time_taken.columns = ['avg_time', 'std_time']

    festival_time_taken = festival_time_taken.reset_index()

    df_aux = np.round(festival_time_taken.loc[festival_time_taken['Festival'] == festival, operacao], 2)


    return df_aux

# ------------------------------------------------------------------------------
# Gerar um fig para gráfico Sunburst - Avg City and Road Traffic Density 
# ------------------------------------------------------------------------------


def avg_std_time_on_traffic(df):
    
    """ Esta função calcula o tempo médio e o desvio padrão de entrega por cidade e por tráfego.
        Inseri as informações em um grafico de explosão solar

    Parâmetros:
       Input:
           - df: Dataframe com os dados necessários para o cálculo
           - operacao: Tipo de operação que precisa ser calculado, sendo elas:
               - 'avg_time': Calcula o tempo médio
               - 'std_time': Calcula o desvio padrão do tempo
       Output:
           - fig de um gráfico de explosão solar (sunburst)

    """

    mean_std_time_taken_by_city_by_road_traffic_density = (df.loc[:, ['Time_taken(min)', 'City', 'Road_traffic_density']]
                                                           .groupby(['City', 'Road_traffic_density'])
                                                           .agg({'Time_taken(min)': ['mean', 'std']}))

    mean_std_time_taken_by_city_by_road_traffic_density.columns = ['avg_time', 'std_time']
    df_aux = mean_std_time_taken_by_city_by_road_traffic_density.reset_index()

    fig = px.sunburst(df_aux, path = ['City', 'Road_traffic_density'],
                      values = 'avg_time',
                      color = 'std_time',
                      color_continuous_scale = 'RdBu',
                      color_continuous_midpoint = np.average(df_aux['std_time']))

    return fig


# ------------------------------------------------------------------------------
# Gerar um fig para gráfico Barra - Erro - Distribuição do Tempo por Cidade
# ------------------------------------------------------------------------------

def avg_std_graph(df):

    """ Esta função calcula o tempo médio e o desvio padrão de entrega por cidade.
        Inseri as informações em um grafico de barra (com a média) com a marcação de erro (desvio padrão).

    Parâmetros:
       Input:
           - df: Dataframe com os dados necessários para o cálculo
           - operacao: Tipo de operação que precisa ser calculado, sendo elas:
               - 'avg_time': Calcula o tempo médio
               - 'std_time': Calcula o desvio padrão do tempol
       Output:
           - fig de um gráfico de barra (com a média) com a marcação de erro (desvio padrão).
    """
    
    mean_std_time_taken_by_city = df.loc[:, ['Time_taken(min)', 'City']].groupby('City').agg({'Time_taken(min)': ['mean', 'std']})

    mean_std_time_taken_by_city.columns = ['avg_time', 'std_time']
    mean_std_time_taken_by_city = mean_std_time_taken_by_city.reset_index()

    fig = go.Figure()
    fig.add_trace( go.Bar( name = 'Control',
                          x = mean_std_time_taken_by_city['City'],
                          y = mean_std_time_taken_by_city['avg_time'],
                          error_y = dict( type = 'data', array = mean_std_time_taken_by_city['std_time'])))

    fig.update_layout(barmode = 'group')

    return fig

# ------------------------------------------------------------------------------
# Gerar um Dataframe com a Distribuição da Distância por Cidade e Tipo de Ordem
# ------------------------------------------------------------------------------

def mean_distance_by_type_of_order_and_city(df):

    """ Esta função calcula o tempo médio e o desvio padrão de entrega por cidade e por tipo de ordem.

    Parâmetros:
       Input:
           - df: Dataframe com os dados necessários para o cálculo
           - operacao: Tipo de operação que precisa ser calculado, sendo elas:
               - 'avg_time': Calcula o tempo médio
               - 'std_time': Calcula o desvio padrão do tempo
       Output:
           - df_aux: dataframe com a agregação de cidade e tipo de ordem, com as métricas média e desvio padrão.
           
    """
    
    mean_std_time_taken_by_city_by_type_of_order = (df.loc[:, ['Time_taken(min)', 'City', 'Type_of_order']]
                                                 .groupby(['City', 'Type_of_order'])
                                                 .agg({'Time_taken(min)': ['mean', 'std']}))

    mean_std_time_taken_by_city_by_type_of_order.columns = ['mean_time_taken', 'std_time_taken']
    df_aux = mean_std_time_taken_by_city_by_type_of_order.reset_index()

    return df_aux

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

# ------------------------------------------------------------------------------
# Criando a primeira Tab
# ------------------------------------------------------------------------------

with tab1:
    
# ------------------------------------------------------------------------------
# Primeiro Container - Métricas em Colunas

    with st.container():
        st.title('Overall Metrics')
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
           
            delivery_unic = df.loc[:, 'Delivery_person_ID'].nunique()
            col1.metric('Entregadores', delivery_unic)
            
        with col2:
            
            avg_distance = distance(df, avg_by_city=False)
            col2.metric('Distância Média', avg_distance)
            
            
        with col3:
            
            df_aux = avg_st_time_delivery(df, 'avg_time', 'Yes')            
            col3.metric('Tempo Médio c/ Festival', df_aux)
                        
            
        with col4:
            
            df_aux = avg_st_time_delivery(df, 'std_time', 'Yes')            
            col4.metric('STD c/ Festival', df_aux)

            
        with col5:
            
            df_aux = avg_st_time_delivery(df, 'avg_time', 'No')            
            col5.metric('Tempo Médio sem Festival', df_aux)

            
        with col6:
            
            df_aux = avg_st_time_delivery(df, 'std_time', 'No')

            col6.metric('STD sem Festival', df_aux)
        
        st.markdown("""---""")

        
# ------------------------------------------------------------------------------
# Segundo Container - Gráfico de Pizza


    with st.container():
        st.title('Tempo médio de entrega')
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('###### Por cidade')
            fig = distance(df, avg_by_city=True)
            st.plotly_chart(fig)
 
            
        with col2:
            st.markdown('###### Por Densidade de Tráfego')
            
            fig = avg_std_time_on_traffic(df)
            st.plotly_chart(fig)

        
    st.markdown("""---""")

# ------------------------------------------------------------------------------
# Terceiro Container

    tab1, tab2 = st.tabs(["📈 Distribuição do tempo", "🗃 Distribuição da distância"])
    with st.container():
        
        with tab1:            
            st.title('Distribuição do tempo')
        
            fig = avg_std_graph(df)    
            st.plotly_chart(fig)
            
        with tab2:
            st.title('Distribuição da distância')
            df_aux = mean_distance_by_type_of_order_and_city(df)
            st.dataframe(df_aux)
            
    st.markdown("""---""")
   