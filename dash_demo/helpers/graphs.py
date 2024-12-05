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