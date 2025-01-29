import numpy as np #importa a biblioteca usada para trabalhar com vetores e matrizes
import pandas as pd #importa a biblioteca usada para trabalhar com dataframes (dados em formato de tabela) e análise de dados
import os
# Import do Arquivo

#Divisão de chunks para a conseguir um melhor gerenciamento de memória
def preproc(id_cidade,nome_cidade):
    chunksize = 15000
    df_chunks = pd.read_csv(os.path.join("Arbolytics v\dataset.csv"), encoding="ISO-8859-1", sep=',', index_col=None, chunksize=chunksize)
    print('Preproc: Dados importados com sucesso!')

    filtered_dfs = []
    print(id_cidade)
    for chunk in df_chunks:
        filtered_chunk = chunk[chunk['ID_MUNICIP'] == id_cidade] 
        filtered_dfs.append(filtered_chunk)   
         
    df = pd.concat(filtered_dfs)

    #Pre-Processamento de dados
    #Removendo as erros de id de unidade
    df = df[df['ID_UNIDADE'] != 9]
    df = df[df['ID_UNIDADE'] != 689]
    df = df[df['ID_UNIDADE'] != 799]
    df = df[df['ID_UNIDADE'] != 1294]

    #Renomeando Id da doença e classificão final.
    df['ID_AGRAVO'] = df['ID_AGRAVO'].replace({'A90':'1', 'A92':'2'})
    df['CLASSI_FIN'] = df['CLASSI_FIN'].replace({'Dengue':'1', 'Chikungunya':'2', 'Discarded/Inconclusive':'3'})

    #Reordenando colunas
    penultima = df.pop('ID_AGRAVO')
    df.insert(55, 'ID_AGRAVO', penultima)

    ultima = df.pop('CLASSI_FIN')
    df.insert(55, 'CLASSI_FIN', ultima)

    #Drop de colunas irrelevantes
    df = df.drop(['DT_NASC' ,'DT_NOTIFIC' ,'DT_SIN_PRI' ,'DT_ENCERRA' ,'DT_INVEST' ],  axis=1)

    #Padronização de tipo de variavel
    df = df.astype({'ID_UNIDADE':'float'})
    df = df.astype({'ID_UNIDADE':'int'})

    print(len(df))

    print('Preproc: Pré-Processamento Concluido') 
    df.to_csv(os.path.join("MontagemDF\ArquivoGerado\dataset_" + nome_cidade +".csv"), index=False)
    print('Preproc: Arquivo Salvo') 
    


    