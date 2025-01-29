import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash
import numpy as np
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from dash_bootstrap_templates import ThemeSwitchAIO
import GetCoord as GetCoord
import os
## TODO
# OK  Resultado de 2014 estranho
# Problema do raio dos discos (Semana anterior?)
# Ajustar colormap pra algum valor estatístico (q2, q3?)
# Ajustar Escala para algum valor estatístico q3+3*iqr?
# OK Problema de alinhamento da semana de notificação: mudar organização da ordem de exibição?
# OK Problema de assimetria na distribuição


app = dash.Dash(__name__,external_stylesheets=[dbc.themes.COSMO])
nome_sistema = 'Arbolytics'

#Opções dropdown
arquivos_na_pasta = os.listdir('MontagemDF\ArquivoGerado\Resultado')
opcoes_dropdown = [{'label': arquivo, 'value': arquivo} for arquivo in arquivos_na_pasta]
opcao_padrao = opcoes_dropdown[0]['value']
#inicializando variaveis globais
global cLati
cLati = -17
global cLong
cLong = -17
global lim_sup
lim_sup =1
global df
global grupo1
df = pd.DataFrame({'X': [0,1,2], 'Y': [0,1,2]})
grupo1 = pd.DataFrame({'X': [0,1,2], 'Y': [0,1,2]})
global cityb 
cityb = opcoes_dropdown[0]['value'].replace('.csv', '')


figura_mapa = px.scatter()
figura_mapa.update_layout(width=400, height=300)
figura_histograma = px.scatter()
figura_histograma.update_layout(width=400, height=300)


GAUSSIAN_DATA = False
dict_semana = []
for i in range(0,54):
    if i < 10:
        digit = '0'
    else:
        digit = ''
    dict_semana.append(digit+str(i))

pd.options.mode.chained_assignment = None 



def abrir_arquivo(nome_cidade_conc):
    global cLati
    global cLong
    global lim_sup
    global df
    global grupo1
    global cityb
    
    # Leitura do arquivo .csv
    df = pd.read_csv(os.path.join("MontagemDF\ArquivoGerado\Resultado", nome_cidade_conc), encoding="ISO-8859-1", sep=',', index_col=None)
    print('Arquivo encontrado', nome_cidade_conc,'.')
    

    # Criação do Grafico de linha
    grupo1 = df.groupby('SEM_NOT').agg({'COUNT':'sum','ANO': 'first', 'SEMANA': 'first'}).reset_index()

    s_q1, s_q2, s_q3 = np.quantile(grupo1.groupby('SEMANA')['COUNT'].transform(calcular_q2), [0.25, 0.5, 0.75])
    lim_sup = s_q3 + 1.5*(s_q3+s_q1)

    grupo1['MIN_VALUE'] = grupo1.groupby('SEMANA')['COUNT'].transform(calcular_min)
    grupo1['MAX_VALUE'] = grupo1.groupby('SEMANA')['COUNT'].transform(calcular_max)
    grupo1['Q1'] = grupo1.groupby('SEMANA')['COUNT'].transform(calcular_q1)
    grupo1['Q3'] = grupo1.groupby('SEMANA')['COUNT'].transform(calcular_q3)

    if (GAUSSIAN_DATA):
        grupo1['MIN_FENCE'] = grupo1.groupby('SEMANA')['COUNT'].transform(calcular_min_fence_gauss)
        grupo1['MAX_FENCE'] = grupo1.groupby('SEMANA')['COUNT'].transform(calcular_max_fence_gauss)
    else:
        grupo1['MIN_FENCE'] = grupo1.groupby('SEMANA')['COUNT'].transform(calcular_min_fence_non_gauss)
        grupo1['MAX_FENCE'] = grupo1.groupby('SEMANA')['COUNT'].transform(calcular_max_fence_non_gauss)

    ###################################### CONTROLE DA CLASSE ######################################
    media_semanal = df.groupby('SEMANA')['COUNT'].mean()

    media_semanal_dict = media_semanal.to_dict()
    df['MEDIA_SEMANAL'] = df['SEMANA'].map(media_semanal_dict)
    df['QUALI'] = 0

    
    fator = 1
    for row in df.index:
        if df['COUNT'][row] <= df['MEDIA_SEMANAL'][row] * fator:
            df['QUALI'][row] = 'Abaixo da Média'
        else:
            df['QUALI'][row] = 'Acima da Média'


    ###################################### CONTROLE DO RAIO ######################################
    for row in df.index:
        if df['COUNT'][row] < 1:
            df['NORM'][row] = 1
        else:
            df['NORM'][row] = df['COUNT'][row]
    ######################################                   ######################################

    figura_histograma = px.line(grupo1,x = "SEM_NOT", y="COUNT",template="plotly_white").update_layout(xaxis_title="Semana de Notificação", yaxis_title="N° Casos")
    cLati,cLong=GetCoord.get_coord(' ',nome_cidade_conc + ', Brasil')
    print('!!!Arquivo encontrado', nome_cidade_conc,'.')

    

# Função minimo e IQR^
def calcular_q0(valores):
    return np.quantile(valores, 0)
    
def calcular_q1(valores):
    v = valores.values    
    median = np.median(v)
    q1 = np.median(np.array(v[np.where(v <= median)]))    
    return q1
    
def calcular_q2(valores):
    v = valores.values    
    median = np.median(v)        
    return median
    
def calcular_q3(valores):
    v = valores.values    
    median = np.median(v)    
    q3 = np.median(np.array(v[np.where(v >= median)]))    
    return q3

def calcular_min(valores):
    if GAUSSIAN_DATA:
        m = calcular_min_fence_gauss(valores)
    else:
        m = calcular_min_fence_non_gauss(valores)
    v = np.array(sorted(valores))
    idx = np.where(v >= m)[0][0]
    return v[idx]

def calcular_max(valores):
    if GAUSSIAN_DATA:
        m = calcular_max_fence_gauss(valores)
    else:
        m = calcular_max_fence_non_gauss(valores)
    v = np.array(sorted(valores))
    idx = np.where(v <= m)[0][-1]
    return v[idx]

def calcular_min_fence_gauss(valores):
    k = 1.5
    #q3, q1 = np.quantile(valores, [.75 , .25])
    q1 = calcular_q1(valores)
    q3 = calcular_q3(valores)
    iqr = q3 - q1
    return max(0,q1 - k * iqr)

def calcular_max_fence_gauss(valores):
    k = 1.5
    #q3, q1 = np.quantile(valores, [.75 , .25])
    q1 = calcular_q1(valores)
    q3 = calcular_q3(valores)
    iqr = q3 - q1
    return q3 + k * iqr

def calcular_min_fence_non_gauss(valores):
    n = 7 # Numero de valores disponíveis (anos) em cada semana epidemiologica
    k2 = ((17.63 * n) - 23.64) / ((7.74*n) - 3.71) # Estimativa dada por CARLING (2000)
    q1 = calcular_q1(valores)
    q2 = calcular_q2(valores)
    q3 = calcular_q3(valores) 
    #q3, q1 = np.quantile(valores, [.75 ,.25])
    iqr = q3 - q1
    #q2 = np.quantile(valores, 0.5) # Mediana
    return max(0,q2 - k2 * iqr)

def calcular_max_fence_non_gauss(valores):
    n = 7 # Numero de valores disponíveis (anos) em cada semana epidemiologica
    k2 = ((17.63 * n) - 23.64) / ((7.74*n) - 3.71) # Estimativa dada por CARLING (2000)
    q1 = calcular_q1(valores)
    q2 = calcular_q2(valores)
    q3 = calcular_q3(valores)
    #q3, q1 = np.quantile(valores, [.75 ,.25])
    iqr = q3 - q1
    #q2 = np.quantile(valores, 0.5) # Mediana
    return q2 + k2 * iqr






app.layout = html.Div(
                    style={'width': '100%', 'display': 'flex'},
                    children=[
                        # coluna da esquerda
                        html.Div(
                        children=[
                            html.H1(children=nome_sistema, style={'font-size': '50px', 'margin': '0 20px','margin-top': '20px'}),
                            # A graphical analysis of the distribution of arboviral cases (Dengue and Chikungunya) along the period 2013-2020.
                            html.Div(children='''                            	
                                Um sistema para análise visual de dados da distribuição de casos arboviroses (Dengue e Chikungunya apenas) ao longo do período de 2013-2020. A aplicação possibilita visualizar tanto o dado do ano escolhido (laranja) quanto estatísticas do histórico do período (tons de cinza).
                            ''', style={'margin': '0 20px'}),
                            # salvar linha
                            html.Br(),  
                            html.Label('Selecione a cidade:', style={'width': '399px', 'text-align': 'left', 'margin': '0px 136px'}),
                            html.Div(
                                style={'width': '399px', 'display': 'flex', 'justify-content': 'left', 'padding-left': '40px'},
                                children=[
                                    dcc.Dropdown(
                                        id='city-dropdown',
                                        options=opcoes_dropdown,
                                        value= opcao_padrao ,
                                        style={'width': '200px', 'color':'black'}
                                    )
                                ]
                            ),                            
                            html.Br(),  
                            html.Label('Selecione o ano:', style={'width': '399px', 'text-align': 'left', 'margin': '0px 136px'}),
                            html.Div(
                                style={'width': '399px', 'display': 'flex', 'justify-content': 'left', 'padding-left': '40px'},
                                children=[
                                    dcc.Dropdown(
                                        id='year-dropdown',
                                        options=[
                                        {'label': '2013', 'value': '2013'},
                                        {'label': '2014', 'value': '2014'},
                                        {'label': '2015', 'value': '2015'},
                                        {'label': '2016', 'value': '2016'},
                                        {'label': '2017', 'value': '2017'},
                                        {'label': '2018', 'value': '2018'},
                                        {'label': '2019', 'value': '2019'},
                                        {'label': '2020', 'value': '2020'},
                                    ],
                                        value=2013,
                                        style={'width': '200px', 'color':'black'}
                                    )
                                ]
                            ),
                        ],
                        style={'flex': '1', 'max-width': '25%', 'height': '100vh', 'float': 'left', 'background-color': '#212121', 'color':'white'}
                    ),

                        # coluna da direita
                        html.Div(
                            style={'flex': '1', 'height': '100vh', 'max-width': '75%'},
                            children=[
                            
                                # grafico 3
                                html.Div(
                                    style={'width': '100%', 'height': '33%'},
                                    children=[
                                        dcc.Graph(
                                            id='histograma',
                                            figure=figura_histograma,
                                            style={'width': '100%', 'height': '100%'}
                                        ),
                                    ]
                                ),
                                
                                # grafico 1
                                html.Div(
                                    style={'width': '100%', 'height': '55%'},#era 60
                                    children=[
                                        dcc.Graph(
                                            id='mapa',
                                            figure=figura_mapa,
                                        )
                                    ]
                                ),
                                
                                
                # grafico 2
                                html.Div(
                                    style={'width': '91%', 'height': '7%', 'padding-left':30},
                                    children=[
                                        html.Div('Semana de notificação'),
                    # slider
                                    dcc.Slider(id='slider-semana', min=1, max=53, step=1, value=1, tooltip={"placement": "bottom", "always_visible": True}, included=False), 
                                    ]
                                ),

                                
                            ],
                        )
                    ],
                )
        
@app.callback(
    [Output('mapa', 'figure'),Output('histograma', 'figure')],
    [Input('year-dropdown', 'value'), Input('slider-semana', 'value'), Input('city-dropdown', 'value')]
)


def update_graph1(year, week, city):
    global cLati
    global cLong
    global lim_sup
    global df
    global grupo1
    global cityb
    year= int(year)

    if(cityb  != city):
        cityb = city
        abrir_arquivo(city)
    

   
    # Criação do mapbox
    filtered_df = df[(df['ANO']) == year]
    filtered_df = filtered_df[filtered_df['SEM_NOT'] == int(str(year) + str(dict_semana[week]))] 
    
    #print(filtered_df['SEMANA_ANTERIOR'])   color_discrete_sequence=["#e41a1c", "#4daf4a", "#377eb8"] new colors #ef8a62 #67a9cf
    color_discrete_mapx = {'Acima da Média': 'rgb(123,50,148)', 'Abaixo da Média': 'rgb(0,136,55)', 'Valor3': 'rgb(103,0,0)'}
    
    
    #if(filtered_df['SEMANA'].values[0] == 1):
    if(len(set(filtered_df['SEMANA_ANTERIOR'].values)) == 1):
        figura_mapa = px.scatter_mapbox(filtered_df, lat="LATI", lon="LONG", color="QUALI",
                            size="SEMANA_ANTERIOR", mapbox_style="carto-positron", color_discrete_map=color_discrete_mapx, zoom=12, size_max= 4, hover_data=['COUNT', 'SEMANA_ANTERIOR','MEDIA_SEMANAL']) #zoom=13, range_color=(1 , 50)
    
    else:
        figura_mapa = px.scatter_mapbox(filtered_df, lat="LATI", lon="LONG", color="QUALI",
                            size="SEMANA_ANTERIOR", mapbox_style="carto-positron", color_discrete_map=color_discrete_mapx, zoom=12, size_max= 15, hover_data=['COUNT', 'SEMANA_ANTERIOR','MEDIA_SEMANAL']) #zoom=13, range_color=(1 , 50)
    
    
    
    #
    figura_mapa.update_layout(paper_bgcolor='#FFFFFF')
    figura_mapa.layout.coloraxis.colorbar.title = 'N° Casos'
    figura_mapa.update_coloraxes(colorbar_bgcolor='#FFFFFF')
    figura_mapa.update_coloraxes(colorbar_tickfont_color='#000000')   
    figura_mapa.update_traces(marker =dict(sizemin = 4))
    figura_mapa.update_layout(mapbox_center = {"lat": cLati, "lon": cLong}, margin=dict(l=0, r=0, t=0, b=0)) # mapbox_zoom=12,  # RIO VERDE
    figura_mapa.update_layout(height=570)
    figura_mapa.update_layout(template="plotly_white",coloraxis_colorbar=dict(title_font=dict(color="black"),tickfont=dict(color="black")))
    figura_mapa["layout"].pop("updatemenus")
    figura_mapa.layout.coloraxis.showscale = True
    figura_mapa.update_layout(legend_title_text='Quantidade de Casos')

    filtered_dfh = grupo1[(grupo1['ANO']) == year]
    intervalos = grupo1 ['SEMANA'].astype(str).tolist()
    
    figura_histograma = go.Figure([
    #linha central lina
    go.Scatter(
        name='Intervalo de limite estatístico (método IQR)',
        x=intervalos,
        y=filtered_dfh['MAX_FENCE'],
        mode='lines',
        line=dict(width=1, dash="dot", color='rgb(150, 150, 150)'),
        showlegend=True,
#        hovertemplate = '<b>Semana:</b> %{x}<br><b>Limite estatístico de casos:</b> %{y:.0f}<extra></extra>',
        hovertemplate = '<b>Limite estatístico de casos:</b> %{y:.0f}<extra></extra>',        
    ),
    go.Scatter(
        name=year,
        x=intervalos,
        y=filtered_dfh['COUNT'],
        mode='lines',
        #mode='markers',
        line=dict(color='rgb(200, 100, 0)'),
        #fillcolor='rgba(200, 100, 0, 0.6)',
        #fill='tonexty',
        hovertemplate = '<b>Total casos:</b> %{y:.0f}<extra></extra>',                        
    ),
    go.Scatter(
        name='Intervalo do máximo casos (sem anomalias)',
        x=intervalos,
        y=filtered_dfh['MAX_VALUE'],
        mode='lines',
        line=dict(width=0, dash="dot", color='rgb(0, 0, 168)'),           
        showlegend=False,
##        hovertemplate = '<b>Semana:</b> %{x}<br><b>Limite estatístico de casos:</b> %{y:.0f}',
        hovertemplate = '<b>Maximo casos (sem anomalias):</b> %{y:.0f}<extra></extra>',        
    ),    
    go.Scatter(
        name='Intervalo de 75% dos casos',
        x=intervalos,
        y=filtered_dfh['Q3'],
        mode='lines',
        line=dict(width=0, dash="solid", color='rgba(68, 68, 68, 0.6)'),
        fillcolor='rgba(68, 68, 68, 0.4)',
        fill='tonexty', 
        showlegend=False,
        hoverinfo='skip',
##        hovertemplate = '<b>Semana:</b> %{x}<br><b>75% casos:</b> %{y:.0f}<extra></extra>',
        hovertemplate = '<b>75% casos:</b> %{y:.0f}<extra></extra>',                        
    ),
    go.Scatter(
        name='Intervalo de 50% dos casos',
        x=intervalos,
        y=filtered_dfh['Q3'],
        mode='lines',
        line=dict(width=0, dash="solid", color='rgba(68, 68, 68, 0.3)'),
        fillcolor='rgba(68, 68, 68, 0.2)',
        fill='tonexty', 
        showlegend=True,
        hoverinfo='skip',
##        hovertemplate = '<b>Semana:</b> %{x}<br><b>75% casos:</b> %{y:.0f}<extra></extra>',
        #hovertemplate = '<b>75% casos:</b> %{y:.0f}<extra></extra>',                        
    ),
    go.Scatter(
        name='Intervalo de 25% dos casos',
        x=intervalos,
        y=filtered_dfh['Q1'],
        line=dict(width=0, dash="solid", color='rgb(68, 68, 68, 0.3)'),
        mode='lines',
        fillcolor='rgba(68, 68, 68, 0.2)',
        fill='tonexty',
        showlegend=False,
        #hoverinfo='skip',
##        hovertemplate = '<b>Semana:</b> %{x}<br><b>25% casos:</b> %{y:.0f}<extra></extra>',
        hovertemplate = '<b>25% casos:</b> %{y:.0f}<extra></extra>',                                
    ),    
    go.Scatter(
        name='Intervalo do total de casos (sem anomalias)',
        x=intervalos,
        y=filtered_dfh['MIN_VALUE'],
        mode='lines',
        line=dict(width=0, dash="dot", color='rgb(168, 0, 0)'),   
        fillcolor='rgba(68, 68, 68, 0.4)',
        fill='tonexty',
        showlegend=True,
##        hovertemplate = '<b>Semana:</b> %{x}<br><b>Limite estatístico de casos:</b> %{y:.0f}',
        hovertemplate = '<b>Minimo casos (sem anomalias):</b> %{y:.0f}<extra></extra>',        
    ),
    go.Scatter(
        name='Intervalo do limite estatístico',
        x=intervalos,
        y=filtered_dfh['MIN_FENCE'],
        mode='lines',
        line=dict(width=1, dash="dot", color='rgb(150, 150, 150)'),      
        showlegend=False,
#        hovertemplate = '<b>Semana:</b> %{x}<br><b>Limite estatístico de casos:</b> %{y:.0f}',
        hovertemplate = '<b>Limite estatístico de casos:</b> %{y:.0f}<extra></extra>',        
    ),         
    ])
    figura_histograma.update_layout(margin=dict(l=20, r=20, t=20, b=0))
    figura_histograma.update_layout(xaxis_title="Semana de Notificação", yaxis_title="N° Casos")
    figura_histograma.update_xaxes(range=[0,53])
    figura_histograma.update_yaxes(range=[0,1500])
    figura_histograma.update_layout(template="plotly_white")
    #figura_histograma.update_traces(hovertemplate=None)
    figura_histograma.update_layout(hovermode="x")
    
    # print(filtered_dfh['COUNT'].head(12))
    # print(filtered_dfh['MAX_VALUE'].head(12))
    # print(filtered_dfh['MIN_VALUE'].head(12))
    app.config.show_undo_redo = False
    return figura_mapa, figura_histograma

app.title = nome_sistema

if __name__ == '__main__':
    app.run_server(debug=False)


