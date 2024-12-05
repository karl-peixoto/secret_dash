import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

c1 = 'rgba(32, 46, 57, 1)'
c2 = "rgba(0, 159, 227, 1)"
c3 = "rgba(190, 215, 51, 1)"
c4 = "rgba(255, 165, 0, 1)"  # Orange color
c5 = "rgba(0, 100, 0, 1)"

# Function to get data from MySQL
def get_data():
    data = pd.read_csv('projeto_dashh_helton/dados/dados_pontos_selecionados.csv')

    #Conversões
    data['tipo'] = data['tipo'].astype(str).str.title()
    data['status'] = data['status'].apply(lambda x: 'Migrados' if x == 'Migração' \
                                          else 'Outros Provedores' if x == 'Other Providers' \
                                            else 'Não Migrados' if x == 'Will Not Migrate' \
                                                else 'Novas Ativações')
    
    data.dropna(subset='latitude', inplace=True)
    return data


def get_usage_data(dados_filtrados):
    usage = pd.read_csv('projeto_dashh_helton/dados/oct_hourly_use.csv')
    usage = usage[usage['mac_address'].isin(dados_filtrados['mac_address'])]
    usage = usage.merge(dados_filtrados, on='mac_address', how='left')
    usage['GBytes_in'] = usage['incomingBytes'].astype(float) / 1024 / 1024 / 1024
    usage['GBytes_out'] = usage['outgoingBytes'].astype(float) / 1024 / 1024 / 1024
    usage['Total'] = usage['incomingBytes'] + usage['outgoingBytes']
    usage['datetime'] = pd.to_datetime(usage[['year', 'month', 'day', 'hour']])
    usage['date'] = usage['datetime'].dt.date

    apps = pd.read_csv('projeto_dashh_helton/dados/oct_apps_use.csv')
    apps = apps[apps['mac_address'].isin(dados_filtrados['mac_address'])]
    apps = apps.merge(dados_filtrados, on='mac_address', how='left')
    apps['GBytes_in'] = apps['incomingBytes'].astype(float) / 1024 / 1024 / 1024 
    apps['GBytes_out'] = apps['outgoingBytes'].astype(float) / 1024 / 1024 / 1024
    apps['Total'] = apps['incomingBytes'] + apps['outgoingBytes']
    apps['cat_1'] = apps['service_object'].apply(lambda x: str(x).split("/")[0])
    apps["cat_2"] = apps["service_object"].apply(lambda x: str(x).split("/")[1] if len(str(x).split("/")) > 1 else "Não informado")
    apps["cat_3"] = apps["service_object"].apply(lambda x: str(x).split("/")[2] if len(str(x).split("/")) > 2 else "Não informado")

    return usage, apps


def main():
    st.title("Gestão de Pontos")
    
    # Load data
    data = get_data()
    st.sidebar.image("projeto_dashh_helton/int_vsat_TM_rgb_wht.png", width=100)
    
    # Sidebar filters
    st.sidebar.header("Opções de Filtro")

    
    # Filtro de Tipo de Ponto
    lista_tipos = data['tipo'].unique()
    selected_tipos = st.sidebar.multiselect("Tipo de Ponto", lista_tipos, default=lista_tipos)
    
    # Filtro de Status
    lista_status = data['status'].unique()
    selected_status = st.sidebar.multiselect("Status", lista_status, default=lista_status)

    lista_final_status = data['final_status'].unique()
    selected_final_status = st.sidebar.multiselect("Final Status", lista_final_status, default=lista_final_status)
    
    # Filter data based on selection
    filtered_data = data[(data['tipo'].isin(selected_tipos)) &\
                          (data['status'].isin(selected_status)) &\
                              (data['final_status'].isin(selected_final_status))].copy()
    

    #Painel de contagens
    st.header('Circuitos Selecionados')
    status_final, status,  modem = st.columns(3)
    planos, tipo = st.columns(2)
    #col1.metric("Total de Pontos", filtered_data.shape[0])

    #Contagem por tipo de ponto
    contagem1 = filtered_data.groupby('tipo')[['old_circuit_id']].count().reset_index()
    contagem1.columns = ['Tipo', 'Total']
    tipo.table(contagem1)

    #Contagem por Status Migração
    contagem2 = filtered_data.groupby('status')[['old_circuit_id']].count().reset_index()
    contagem2.columns = ['Status', 'Total']
    status.table(contagem2)

    #Contagem por Status Final
    contagem3 = filtered_data.groupby('final_status')[['old_circuit_id']].count().reset_index()
    contagem3.columns = ['Status Final', 'Total']
    status_final.table(contagem3)

    #Contagem por tipo de Plano
    contagem4 = filtered_data.groupby('plan')[['old_circuit_id']].count().reset_index()
    contagem4.columns = ['Plano', 'Total']
    planos.table(contagem4)

    #Contagem por tipo de Modem
    contagem5 = filtered_data.groupby('modem')[['old_circuit_id']].count().reset_index()
    contagem5.columns = ['Modem', 'Total']
    modem.table(contagem5)

    #Apresentação do mapa
    st.header('Mapa dos Pontos Selecionados')
    if 'latitude' in filtered_data.columns and 'longitude' in filtered_data.columns:
        st.map(filtered_data[['latitude', 'longitude']])
    else:
        st.write("Dados de latitude e longitude não disponíveis.")



    # Possible Deactivations
    st.header('Análise de Vencimento dos 60 Meses')
    filtered_data['semester'] = pd.to_datetime(filtered_data['terminated_at']).dt.to_period('6M')

    # Group by the semester of deactivation
    grouped_data = filtered_data.groupby('semester')[['old_circuit_id']].count().reset_index()
    grouped_data.columns = ['Semester', 'Total']

    # Create a complete range of semesters
    min_semester = filtered_data['semester'].min()
    max_semester = filtered_data['semester'].max()
    all_semesters = pd.period_range(start=min_semester, end=max_semester, freq='6M')
    all_semesters_df = pd.DataFrame(all_semesters, columns=['Semester'])

    # Merge the grouped data with the complete range to fill in missing periods
    complete_data = pd.merge(all_semesters_df, grouped_data, on='Semester', how='left').fillna(0)

    # Convert the 'Semester' column back to string for plotting
    complete_data['Semester'] = complete_data['Semester'].astype(str)

    # Create a bar graph
    fig4 = px.bar(complete_data, x='Semester', y='Total', title='Número de Desconexões por Semestre', color_discrete_sequence=[c2])
    fig4.update_layout(xaxis_title='Semestre', yaxis_title='Número de Desconexões')

    # Add ticks for each semester
    fig4.update_xaxes(tickvals=complete_data['Semester'], ticktext=complete_data['Semester'])

    st.plotly_chart(fig4)



    st.header('Dados de Consumo')
    get_usage = st.button('Obter Dados de Uso')


    if get_usage:
        #Contadores
        usage, apps = get_usage_data(filtered_data)
        total_terminais, total_download, total_upload = st.columns(3)
        media_download_usuario, media_upload_usuario = st.columns(2)

        total_users = usage['mac_address'].nunique()

        total_terminais.metric("Total de Terminais", total_users)
        total_download.metric("Total de Download (TB)", round(usage['GBytes_in'].sum()/1024, 2))
        total_upload.metric("Total de Upload (TB)", round(usage['GBytes_out'].sum()/1024, 2))
        
        media_download_usuario.metric("Média de Download por Usuário (GB)", round(usage['GBytes_in'].sum()/total_users, 2))
        media_upload_usuario.metric("Média de Upload por Usuário (GB)", round(usage['GBytes_out'].sum()/total_users, 2))
        
        
        #Gráficos
        graficos = st.columns(1)
        media_usuarios = usage.groupby(['old_circuit_id']).agg({'Total': 'sum'}).reset_index()
        media_usuarios['Total'] = media_usuarios['Total'] / 1024 / 1024 / 1024  
        fig = px.histogram(media_usuarios, x="Total", title='Total por Usuário', color_discrete_sequence= [c2], nbins=20)
        fig.update_layout(yaxis_title = 'Nº de Usuários', xaxis_title = 'Consumo em GBytes', autosize=False, width=600, height=500)
        st.plotly_chart(fig)


        #Grafico por dia do mes
        a1 = usage.groupby(['date']).agg({'Total':'sum'}).reset_index()
        a1['Total'] = a1['Total'] / 1024 ** 4

        fig2 = px.bar(a1, x='date', y='Total', title = 'Consumo de dados por dia do mês', color_discrete_sequence= [c2])

        fig2.add_hline(y=a1['Total'].mean(), line_width=3, line_dash="dash", line_color=c4)
        fig2.update_xaxes(showgrid=True,  tickangle = 45)
        fig2.update_layout(xaxis_title = 'Semana do Ano', yaxis_title = 'Consumo (TBytes)', legend_title = 'Detalhe')
        fig2.update_xaxes(tickformat="%d-%m-%Y", dtick=172800000)
        #fig.update_layout(xaxis2=dict(showgrid=True, overlaying='x', side='bottom', anchor='free', position=0.5, title='Mês'))
        st.plotly_chart(fig2)

        #Grafico de consumo por plano
        a3 = usage.groupby(['old_circuit_id']).agg({'Total':'sum', 'plan':'last'}).reset_index()
        a3['Total'] = a3['Total'] / (1024 ** 3)

        fig3 = px.box(a3, x='plan', y='Total', title='Consumo por Plano', color='plan', color_discrete_sequence=px.colors.qualitative.Set2)
        fig3.update_layout(xaxis_title='Plano', yaxis_title='Consumo (GBytes)')
        st.plotly_chart(fig3)
 

        #Consumo por categoria
        cat1_consumption = apps.groupby('cat_1').agg({'Total': 'sum'}).reset_index()
        cat1_consumption['Total'] = cat1_consumption['Total'] / 1024 / 1024 / 1024  # Convert to GBytes
        cat1_consumption = cat1_consumption[cat1_consumption['cat_1'] != 'nan']

        # Ordenar pelo consumo total
        cat1_consumption = cat1_consumption.sort_values(by='Total', ascending=False)

        # Criar o gráfico de barras
        fig5 = px.bar(cat1_consumption, x='cat_1', y='Total', title='Consumo por Categoria (cat_1)', color='cat_1', color_discrete_sequence=[c2])
        fig5.update_layout(xaxis_title='Categoria', yaxis_title='Consumo (GBytes)', coloraxis_showscale=False)
        st.plotly_chart(fig5)

        # Top 10 apps com maior uso total
        top_apps = apps.groupby('cat_3').agg({'Total': 'sum'}).reset_index()
        lista = ['Não informado']
        top_apps = top_apps[~top_apps['cat_3'].isin(lista)]
        top_apps['Total'] = top_apps['Total'] / 1024 / 1024 / 1024  # Convert to GBytes
        top_apps = top_apps.sort_values(by='Total', ascending=False).head(10)

        # Criar o gráfico de barras para os top 10 apps
        fig6 = px.bar(top_apps, x='cat_3', y='Total', title='Top 10 Apps por Consumo Total', color='cat_3', color_discrete_sequence=px.colors.qualitative.Set3)
        fig6.update_layout(xaxis_title='App', yaxis_title='Consumo (GBytes)', coloraxis_showscale=False)
        st.plotly_chart(fig6)


        # Contas ativas sem uso nos últimos 5 dias
        st.header('Contas Ativas sem uso nos últimos 5 dias')
        last_5_days = usage['date'].max() - datetime.timedelta(days=5)
        recent_usage = usage[usage['date'] > last_5_days]
        a5  = usage.groupby(['mac_address', 'old_circuit_id', 'plan', 'tipo', 'final_status', 'status', 'terminated_at'])\
            .agg({'incomingBytes':'sum', 'outgoingBytes':'sum', 'Total':'sum'}).reset_index()
        a5['GBytes_in_mes'] = a5['incomingBytes'] / 1024 / 1024 / 1024
        a5['GBytes_out_mes'] = a5['outgoingBytes'] / 1024 / 1024 / 1024
        a5['Total_mes'] = a5['Total'] / 1024 / 1024 / 1024
        no_usage_accounts = a5[(~a5['mac_address'].isin(recent_usage['mac_address']))\
                                            & (a5['final_status'] == 'Ativo')]
        
        st.write(no_usage_accounts[['old_circuit_id', 'tipo', 'status', 'final_status', 'GBytes_in_mes', 'GBytes_out_mes', 'Total_mes', 'terminated_at', 'plan']])
 

if __name__ == "__main__":
    main()