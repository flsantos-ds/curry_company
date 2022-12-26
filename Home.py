import streamlit as st
from PIL import Image

st.set_page_config(
    page_title = 'Home',
    page_icon = '🏠',
    layout = 'wide')

# image_path = '/Users/fabioldossantos/Documents/repos/ftc_programacao_python/'
image = Image.open('logo.png')
st.sidebar.image(image, width = 180)

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.write('# Curry Company Growth Dashboard')
st.markdown(
    """
    Growth Dashboard foi construído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
    - Visão Empresa:
        - Visão Gerencial: Méticas gerais de comportamento.
        - Visão Tática: Indicadores semanais de crescimento.
        - Visão Geográfica: Insights de geolocalização.
    - Visão Entregadores:
         - Acompanhamento dos indicadores semanais de crescimento.
    - Visão Restaurante:
        - Indicadores semanais de crecimento dos restaurantes.
        
    ### Ask for Help
    - Time de Data Science no Discord
    @FabioLuizDosSantos

    """)
