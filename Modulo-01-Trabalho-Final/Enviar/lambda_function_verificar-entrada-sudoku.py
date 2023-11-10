import json
import boto3
import csv
import io
import numpy as np
import pandas as pd

# Ligacao com o S3
S3Client = boto3.client('s3')
S3Resource = boto3.resource('s3')

def lambda_handler(event, context):

    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    nome = key[9:-4] + "_validado"
    
    # print(bucket)
    # print(key)
    # print(nome)
    
    response = S3Client.get_object(Bucket=bucket, Key=key)
    
    df = pd.read_csv(response['Body'], sep=',', header=None)
    # print(df)

    log = f"{bucket}\n{key}\n{nome}\n\n{df.to_string(index=False, header=False)}\n\n"
    
    log = verificacoes_sudoku(log, df)
    # print(log)
    if log[-2:] == "OK":
        # print("Tudo ok")
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False, header=False)
        S3Resource.Bucket(bucket).put_object(Key="validados/" + nome + ".csv", Body=csv_buffer.getvalue())
    
    utf_log = log.encode("utf-8")
    S3Resource.Bucket(bucket).put_object(Key="validados/" + nome + ".txt", Body=utf_log)
    return {"statusCode": 200}
    
# Fazer as verificacoes do arquivo de entrada:
def verificacoes_sudoku(log, df):
    try:
        # Verificacao do tamanho
        if df.shape != (9, 9):
            log += "Sudoku Invalido: Tamanho anormal.\n"
            return log
        else:
            log += "O sudoku tem o tamanho normal\n"
            
        # Verificar se ha apenas valores entre 0 e 9:
        intervalo = (df >= 0) & (df <= 9)
        if intervalo.all().all():
            log += "Todos os elementos do Sudoku estão entre 0 e 9.\n"
        else:
            log += "Pelo menos um elemento do DataFrame está fora do intervalo de 0 a 9.\n"
            return log
            
        # Transforma os valores 0 para None:
        sudoku_df = df.map(lambda x: None if x == 0 else x)
        # print(sudoku_df)

        # Verifica se o jogo veio com elementos repetidos
        elementos_iguais = {'linha':[], 'coluna':[], 'quadrante':[]}
        for i in range(9):
            # Verifica elementos repetidos na linha
            linha = sudoku_df.iloc[i]
            if linha[linha.notnull()].duplicated().any():
                elementos_iguais['linha'].append(i)

            # Verifica elementos repetidos na coluna
            coluna = sudoku_df.iloc[:, i]
            if coluna[coluna.notnull()].duplicated().any():
                elementos_iguais['coluna'].append(i)
        # Verifica elementos repetidos no quadrante
        for i in range(3):
            for j in range(3):
                quadrante = sudoku_df.iloc[i*3:i*3+3, j*3:j*3+3]
                valores_nao_nulos = quadrante.stack().dropna()
                if valores_nao_nulos.duplicated().any():
                    elementos_iguais['quadrante'].append((i, j))
                    # print(elementos_iguais)

        # Confere se houver erro:
        if len(elementos_iguais['linha']) == 0 and len(elementos_iguais['coluna']) == 0 and len(elementos_iguais['quadrante']) == 0:
            log += "O Sudoku não apresenta erros de repetição.\n"
        else:
            log += "O sudoku apresenta valores repetidos nos seguintes locais:\n"
            if len(elementos_iguais['linha']) != 0:
                for aux in elementos_iguais['linha']:
                    log += f"\t Linha {aux}\n"
            if len(elementos_iguais['coluna']) != 0:
                for aux in elementos_iguais['coluna']:
                    log += f"\t Coluna {aux}\n"
            if len(elementos_iguais['quadrante']) != 0:
                for aux in elementos_iguais['quadrante']:
                    log += f"\t Quadrante {aux}\n"
            return log
        log += "OK"
        return log

    except Exception as error:
        print(error)