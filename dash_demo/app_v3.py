import sys
sys.path.append('dash_demo/')

import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
#from dash_demo.helpers.graphs import *
#from dash_demo.helpers.custom_elements import *
#from dash_demo.statics.visuals import *
import folium
from streamlit_folium import folium_static

## GAMBIARRAS
css = """
.legend {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-top: 20px;
}
.legend-item {
    display: flex;
    align-items: center;
    margin-right: 20px;
}
.legend-color {
    width: 20px;
    height: 20px;
    margin-right: 5px;
}
div[data-testid="metric"] {
    display: flex;
    justify-content: center;
    align-items: center;
    text-align: center;
}
/* Centralizar o texto dentro das métricas */
.metric-container {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    padding: 10px;
    margin: 10px;
}
.metric-title {
    font-size: 2em;
    font-weight: bold;
}
.metric-value {
    font-size: 4em;
    font-weight: bold;
}
h1, h2, h3, h4, h5, h6 {
    text-align: center;
}
"""
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

icon_dict = {
    'Escola': 'glyphicon glyphicon-education',
    'UBS': 'glyphicon glyphicon-plus-sign',
    'Povos Originários': 'glyphicon glyphicon-home',
    'Outros': 'glyphicon glyphicon-map-marker'
}
color_dict = {
    'Online': 'green',
    'Offline': 'red',
    'Atenção': 'orange'
}


legenda1 = """
<div class="legend">
    <div class="legend-item">
        <div class="legend-color" style="background-color: rgba(190, 215, 51, 1);"></div>
        <span>Ativo</span>
    </div>
    <div class="legend-item">
        <div class="legend-color" style="background-color: rgba(0, 159, 227, 1);"></div>
        <span>Bloqueados</span>
    </div>
    <div class="legend-item">
        <div class="legend-color" style="background-color: rgba(32, 46, 57, 1);"></div>
        <span>Terminated</span>
    </div>
    <div class="legend-item">
        <div class="legend-color" style="background-color: rgba(255, 165, 0, 1);"></div>
        <span>Grace</span>
    </div>
    <div class="legend-item">
        <div class="legend-color" style="background-color: rgba(0, 100, 0, 1);"></div>
        <span>Reduced</span>
    </div>
</div>
"""

legenda2 = """
<div class="legend">
    <div class="legend-item">
        <div class="legend-color" style="background-color: rgba(190, 215, 51, 1);"></div>
        <span>Online</span>
    </div>
    <div class="legend-item">
        <div class="legend-color" style="background-color: rgba(0, 159, 227, 1);"></div>
        <span>Atencao</span>
    </div>
    <div class="legend-item">
        <div class="legend-color" style="background-color: rgba(32, 46, 57, 1);"></div>
        <span>Offline</span>
    </div>
</div>
"""

import plotly.express as px

c1 = 'rgba(32, 46, 57, 1)'
c2 = "rgba(0, 159, 227, 1)"
c3 = "rgba(190, 215, 51, 1)"
c4 = "rgba(255, 165, 0, 1)"  # Orange color
c5 = "rgba(0, 100, 0, 1)"
cores = [c3, c2, c1, c4, c5]

def grafico_status(df, title):
    df = df[df['new_tipo'] == title]
    fig = px.pie(df, values='old_circuit_id', names='final_status',
                  color='final_status',
                  color_discrete_map={'Ativo':c3, 'Bloqueados':c2, 'Terminated': c1, 'Grace':c4, 'Reduced':c5})
    fig.update_layout(
        title = {'text':title, 'x':0.3},
        autosize=False, width=400, height=320,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False
    )
    fig.update_traces(textinfo='value+percent', textposition='inside')
    return fig

def grafico_atividade(df, title):
    df = df[df['new_tipo'] == title]
    fig = px.pie(df, values='old_circuit_id', names='categoria',
                  color='categoria',
                  color_discrete_map={'Online':c3, 'Atenção':c2, 'Offline': c1, 'Grace':c4, 'Reduced':c5})
    fig.update_layout(
        title = {'text':title, 'x':0.3},
        autosize=False, width=400, height=320,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False
    )
    fig.update_traces(textinfo='value+percent', textposition='inside')
    return fig


def central_metric(label, value):
    st.markdown(f"""
        <div class="metric-container">
            <div class="metric-title">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
    """, unsafe_allow_html=True)


# Function to get data from MySQL
def get_data():
    data = pd.read_csv('dash_demo/dados/dados_pontos_selecionados.csv')

    #Conversões
    data['tipo'] = data['tipo'].astype(str).str.title()
    data['status'] = data['status'].apply(lambda x: 'Migrados' if x == 'Migração' \
                                          else 'Outros Provedores' if x == 'Other Providers' \
                                            else 'Não Migrados' if x == 'Will Not Migrate' \
                                                else 'Novas Ativações')
    
    data.dropna(subset='latitude', inplace=True)
    return data

def get_usage_data(dados_filtrados):
    usage = pd.read_csv('dash_demo/dados/oct_hourly_use.csv')
    usage = usage[usage['mac_address'].isin(dados_filtrados['mac_address'])]
    usage = usage.merge(dados_filtrados, on='mac_address', how='left')
    usage['GBytes_in'] = usage['incomingBytes'].astype(float) / 1024 / 1024 / 1024
    usage['GBytes_out'] = usage['outgoingBytes'].astype(float) / 1024 / 1024 / 1024
    usage['Total'] = usage['incomingBytes'] + usage['outgoingBytes']
    usage['datetime'] = pd.to_datetime(usage[['year', 'month', 'day', 'hour']])
    usage['date'] = usage['datetime'].dt.date

    apps = pd.read_csv('dash_demo/dados/oct_apps_use.csv')
    apps = apps[apps['mac_address'].isin(dados_filtrados['mac_address'])]
    apps = apps.merge(dados_filtrados, on='mac_address', how='left')
    apps['GBytes_in'] = apps['incomingBytes'].astype(float) / 1024 / 1024 / 1024 
    apps['GBytes_out'] = apps['outgoingBytes'].astype(float) / 1024 / 1024 / 1024
    apps['Total'] = apps['incomingBytes'] + apps['outgoingBytes']
    apps['cat_1'] = apps['service_object'].apply(lambda x: str(x).split("/")[0])
    apps["cat_2"] = apps["service_object"].apply(lambda x: str(x).split("/")[1] if len(str(x).split("/")) > 1 else "Não informado")
    apps["cat_3"] = apps["service_object"].apply(lambda x: str(x).split("/")[2] if len(str(x).split("/")) > 2 else "Não informado")

    return usage, apps

# Functions of the layout elements
def introducao(data):
    d1,d2,central,d4,d5 = st.columns(5)
    with central:
        st.title('Pontos Totais')
        central_metric('Quantidade Total de Pontos', len(data))
    st.markdown("<hr>", unsafe_allow_html=True)

#
def analises_iniciais(data):

    st.title('Pontos por Tipo')
    #Definindo colunas
    ubs, esc, orig, out = st.columns(4)
    # Visualizando métricas
    with ubs:
        central_metric(' UBS', len(data[data['new_tipo'] == 'UBS']))
    with esc:
        central_metric('Escolas', len(data[data['new_tipo'] == 'Escola']))
    with orig:
        central_metric('Povos Originários', len(data[data['new_tipo'] == 'Povos Originários']))
    with out:
        central_metric('Outros', len(data[data['new_tipo'] == 'Outros']))



    #Criando Gráficos
    analise = data.groupby(['new_tipo', 'final_status']).count()[['old_circuit_id']].reset_index()
    ubs_g1 = grafico_status(analise, 'UBS')
    esc_g1 = grafico_status(analise, 'Escola')
    orig_g1 = grafico_status(analise, 'Povos Originários')
    out_g1 = grafico_status(analise, 'Outros')    

    st.title('Pontos Existentes na Base e Status')
    # Legenda do Gráfico
    st.markdown(legenda1, unsafe_allow_html=True)

    g1, g2, g3, g4 = st.columns(4)
    # Visualizando gráficos
    with g1:
        st.plotly_chart(ubs_g1)
    with g2:
        st.plotly_chart(esc_g1)
    with g3:
        st.plotly_chart(orig_g1)
    with g4:
        st.plotly_chart(out_g1)

    # Adicionando uma divisória final
    st.markdown("<hr>", unsafe_allow_html=True)

#
def analise_atividade(data):
    data['categoria'] = data['days_since_use'].apply(lambda x: 'Online' if x <= 3 else 'Atenção' if x <= 5 else 'Offline')
    analise = data.groupby(['new_tipo', 'categoria']).count()[['old_circuit_id']].reset_index()
    
    #Criando Gráficos
    ubs_g2 = grafico_atividade(analise, 'UBS')
    esc_g2 = grafico_atividade(analise, 'Escola')
    orig_g2 = grafico_atividade(analise, 'Povos Originários')
    out_g2 = grafico_atividade(analise, 'Outros')

    st.title('Atividade dos Pontos')
    # Legenda do Gráfico
    st.markdown(legenda2, unsafe_allow_html=True)
    g1, g2, g3, g4 = st.columns(4)
    # Visualizando gráficos
    with g1:
        st.plotly_chart(ubs_g2)
    with g2:
        st.plotly_chart(esc_g2)
    with g3:
        st.plotly_chart(orig_g2)
    with g4:
        st.plotly_chart(out_g2)
    
    # Adicionando uma divisória final
    st.markdown("<hr>", unsafe_allow_html=True)


def mapa(data):
    st.title('Mapa dos Pontos')
    filtros, mapa = st.columns(2)
    new_tipo_options = data['new_tipo'].unique().tolist()
    use_cat_options = data['use_cat'].unique().tolist()

    selected_new_tipo = filtros.multiselect("Selecione tipo de ponto", new_tipo_options, default=new_tipo_options)
    selected_use_cat = filtros.multiselect("Selecione uso", use_cat_options, default=use_cat_options)

    # Filter data based on selections
    filtered_data = data[(data['new_tipo'].isin(selected_new_tipo)) & (data['use_cat'].isin(selected_use_cat))]

    # Calculate the average latitude and longitude for centering the map
    avg_lat = filtered_data['latitude'].mean()
    avg_lon = filtered_data['longitude'].mean()

    # Create a map centered at the average coordinates
    mymap = folium.Map(location=[avg_lat, avg_lon], zoom_start=5, maptype='OpenStreetMap')

    filtered_data = filtered_data.dropna(subset='latitude')
    for idx, row in filtered_data.iterrows():
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=f"Circuit ID: {row['new_circuit_id']}",
            icon=folium.Icon(icon=icon_dict.get(row['new_tipo'], 'glyphicon glyphicon-map-marker'),
                            color=color_dict.get(row['use_cat'], 'blue'))
        ).add_to(mymap)
    
    with mapa:
        folium_static(mymap)


def main():
    data = get_data()
    #Introdução dos Pontos Totais
    introducao(data)    

    #Primeiros Gráficos
    analises_iniciais(data)

    #Análise de Atividade
    analise_atividade(data)

    #Análise de Uso
    mapa(data)
    
if __name__ == "__main__":
    main()