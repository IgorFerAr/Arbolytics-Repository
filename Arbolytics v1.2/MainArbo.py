#imports dos files
import GetCoord as GetCoord
import GetNameUni as GetNameUni
import Preproc as Preproc
import GraphBuilder as GraphBuilder
import dash
import dash_bootstrap_components as dbc
#libs
import numpy as np 
import pandas as pd
import plotly.express as px
from itertools import product
import os

import time

def db_count(nome_cidade_conc):
    dfc = pd.read_csv( os.path.join("MontagemDF\ArquivoGerado", "dataset_" + nome_cidade_conc + ".csv"), encoding="ISO-8859-1", sep=',', index_col=None) 
                      
    dfc2 = dfc.pivot_table(index = ['ID_UNIDADE', 'SEM_NOT'], aggfunc ='size')
    
    #transformar id em coord
    dfc2.to_csv(os.path.join("MontagemDF\ArquivoGerado", "counttable_" + nome_cidade_conc +".csv"))

app = dash.Dash(__name__,external_stylesheets=[dbc.themes.COSMO])
pd.options.mode.chained_assignment = None
anos = range(2013, 2021)
semanas = range(1, 54)
print("MainArbo: Sistema Iniciado.")
nome_cidade = input("Digite o nome da cidade: ")
id_cidade = input("Digite o ID da cidade: ")
if(int(id_cidade) > 999999):
    id_cidade = int(str(id_cidade)[:-1])

inicio = time.time()

def transforma_string(texto):
    palavras = texto.split()

    palavras_formatadas = [palavra.capitalize() for palavra in palavras]

    resultado = ''.join(palavras_formatadas)

    return resultado

nome_cidade_conc = transforma_string(nome_cidade)
#print("Nome da cidade: ",nome_cidade_conc)
#print("ID da cidade: ",id_cidade)



if os.path.exists("MontagemDF\ArquivoGerado\dataset_" + nome_cidade_conc +".csv"):
    print("MainArbo: Arquivo datasetPP.csv encontrado.")
else:
    print("MainArbo: Arquivo dataset_" + nome_cidade_conc +".csv NÃO encontrado.")
    print("MainArbo: Montando arquivo datasetPP_" + nome_cidade_conc +".csv.")
    Preproc.preproc(id_cidade,nome_cidade_conc)
    print("MainArbo: Arquivo datasetPP_" + nome_cidade_conc +".csv montado.")

if os.path.exists("MontagemDF\ArquivoGerado\Counttable_" + nome_cidade_conc +".csv"):
    print("MainArbo: Arquivo counttable_" + nome_cidade_conc +".csv encontrado.")
else:
    print("MainArbo: Arquivo counttable_" + nome_cidade_conc +".csv NÃO encontrado.")
    print("MainArbo: Montando arquivo counttable_" + nome_cidade_conc +".csv.")
    db_count(nome_cidade_conc)
    print("MainArbo: Arquivo counttable_" + nome_cidade_conc +".csv montado.")

if os.path.exists("MontagemDF\ArquivoGerado\\" + nome_cidade_conc + ".csv" ):
    print("MainArbo: Arquivo " + nome_cidade_conc +".csv encontrado.")
else:
   
    print("MainArbo: Arquivo " + nome_cidade_conc +".csv NÃO encontrado.")
    print("MainArbo: Montando arquivo " + nome_cidade_conc +".csv.")
        # import
    df = pd.read_csv( os.path.join("MontagemDF\ArquivoGerado", "counttable_" + nome_cidade_conc +".csv"), encoding="ISO-8859-1", sep=',', index_col=None) 

    #transformar id em coord
    df.rename(columns={'0':'COUNT'}, inplace=True)

    df = df[df['ID_UNIDADE'] >= 1000000]

    mux = pd.MultiIndex.from_product([df['SEM_NOT'].unique(), df['ID_UNIDADE'].unique()], names=('SEM_NOT','ID_UNIDADE'))
    df = df.set_index(['SEM_NOT','ID_UNIDADE']).reindex(mux).reset_index()

    # Separação ano semana
    df['SEM_NOT'] = df['SEM_NOT'].astype(int)

    df['ANO'] = df['SEM_NOT'] / 100
    df['ANO'] = df['ANO'].astype(int)

    df['SEMANA'] = df['SEM_NOT'] - (df['ANO'] * 100)
    df['SEMANA'] = df['SEMANA'].astype(int)

    ##########
    all_combinations = pd.DataFrame(list(product(df['ID_UNIDADE'].unique(), range(2013, 2021), range(1, 54))),
                                    columns=['ID_UNIDADE', 'ANO', 'SEMANA'])


    # Combinar as combinações possíveis com os registros existentes
    df = pd.merge(all_combinations, df, on=['ID_UNIDADE', 'ANO', 'SEMANA'], how='outer')

    # Preencher as quantidades ausentes com zero
    df['COUNT'].fillna(0, inplace=True)

    for row in df.index:
        if  np.isnan( df['SEM_NOT'][row]) <= 2:
            df['SEM_NOT'][row] = (df['ANO'][row]*100) + df['SEMANA'][row]
        else:
            df['SEM_NOT'][row] = int(df['SEM_NOT'][row])

    #########
    df.insert(0, "LONG", 1.0)
    df.insert(0, "LATI", 1.0)


    for row in df.index:
        if np.isnan( df['COUNT'][row]):
            df['COUNT'][row] = 0
        else:
            df['COUNT'][row] = int(df['COUNT'][row])

            
    df.sort_values(by = 'ID_UNIDADE', inplace = True)

    print("Tempo:")
    fim = time.time()
    print(fim - inicio)

    idcompare = 000000
    for row in df.index:
        id = df['ID_UNIDADE'][row]

        if id == idcompare:
            df['LATI'][row] = resultado[0]
            df['LONG'][row] = resultado[1]
        else:
            resultado = GetCoord.get_coord(GetNameUni.get_nome(id_cidade,int(df['ID_UNIDADE'][row])), nome_cidade)
            df['LATI'][row] = resultado[0]
            df['LONG'][row] = resultado[1]
            idcompare = id
            
    df.sort_values(by = 'SEM_NOT', inplace = True)

    ###################################### CONTROLE DO RAIO ######################################
    #dividir o norm para controlar tamanho
    norm = df['COUNT']
    df.insert(4, 'NORM', norm)
    
    for row in df.index:
        if df['COUNT'][row] <= 5:
            df['NORM'][row] = 5
        else:
            if df['COUNT'][row] <= 10:
                df['NORM'][row] = 10
            else:
                df['NORM'][row] = 15


    # Agrupamento de valoroes Casos/Semana
    df = df.sort_values(['ID_UNIDADE','SEM_NOT'])
    df['SEMANA_ANTERIOR'] = df.groupby('ID_UNIDADE')['COUNT'].shift()



    for row in df.index:
        if df['SEMANA_ANTERIOR'][row] == 0:
            df['SEMANA_ANTERIOR'][row] = 1


    df = df.fillna(1)
    
    # Agrupamento de valoroes Casos/Semana
    df = df.sort_values(['ID_UNIDADE','SEM_NOT'])
    df['SEMANA_ANTERIOR'] = df.groupby('ID_UNIDADE')['COUNT'].shift()

    df = df.fillna(1)


    #CONTROLE TAMANHO MINIMO
    for row in df.index:
        if df['SEMANA_ANTERIOR'][row] <= 1:
            df['SEMANA_ANTERIOR'][row] = 1

    # Separação ano semana
    df['SEM_NOT'] = df['SEM_NOT'].astype(int)

    df['ANO'] = df['SEM_NOT'] / 100
    df['ANO'] = df['ANO'].astype(int)
    df['SEMANA'] = df['SEM_NOT'] - (df['ANO'] * 100)
    df['SEMANA'] = df['SEMANA'].astype(int)
                      

    df = df.reset_index(drop = True)   
    df.to_csv(os.path.join("MontagemDF\ArquivoGerado\Resultado",  nome_cidade_conc +".csv"),index=False)                    
    print("MainArbo: Arquivo " + nome_cidade_conc +".csv montado.")
    
    print("Tempo:")
    fim = time.time()
    print(fim - inicio)
    print("Finalizada a Execução")




