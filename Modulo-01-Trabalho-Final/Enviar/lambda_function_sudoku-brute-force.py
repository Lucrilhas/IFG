import boto3
import csv
import io
import numpy as np
import pandas as pd

# Ligacao com o S3
S3Client = boto3.client('s3')
s3_resource = boto3.resource('s3')

def lambda_handler(event, context):
    # print(event)
    # print(context)
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    nome = key[10:-13] + "_resultado"
    
    response = S3Client.get_object(Bucket=bucket, Key=key)
    df = pd.read_csv(response['Body'], sep=',', header=None)
    # print(df)
    graph = df.to_numpy(dtype=np.int8)
    # print(graph)
    if solve_sudoku(graph):
        print("Solução encontrada:")
        print_sudoku(graph)
        df_resultado = pd.DataFrame(data=graph, columns=None, index=None)
        csv_buffer = io.StringIO()
        df_resultado.to_csv(csv_buffer, index=False, header=False)
        s3_resource.Bucket(bucket).put_object(Key="resultados/F_Bruta/" + nome + ".csv", Body=csv_buffer.getvalue())
    else:
        print("Não foi possível encontrar uma solução.")
    
    return {'statusCode': 200}
    

# Verifica se e valido colocar
def is_valid(board, lin, col, num):
    # Linha
    if num in board[lin]:
        return False

    # Coluna
    if num in [board[i][col] for i in range(9)]:
        return False

    # Quadrante
    lin, col = 3 * (lin // 3), 3 * (col // 3)
    for i in range(3):
        for j in range(3):
            if board[lin + i][col + j] == num:
                return False

    return True

def solve_sudoku(board):
    for lin in range(9):
        for col in range(9):
            if board[lin][col] == 0:
                for num in range(1, 10):
                    if is_valid(board, lin, col, num):
                        board[lin][col] = num
                        if solve_sudoku(board):
                            return True
                        board[lin][col] = 0  # Do inicio se nao funcionar
                return False
    return True

def print_sudoku(board):
    output = ''
    for row in board:
        output += ' '.join(map(str, row)) + '\n'
    print(output)