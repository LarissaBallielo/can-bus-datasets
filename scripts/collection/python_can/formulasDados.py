import can
import csv
import pandas as pd
from Pid import Pid

"""
formulasDados.py: carrega os PIDs a partir de um arquivo CSV, transformando
cada linha da tabela numa instância de Pid pronta pra usar.
 
Manter isso separado do resto do código significa que adicionar um PID novo
no projeto é só acrescentar uma linha no CSV -- nenhuma linha de código
Python precisa mudar.
"""
 
 

def ler_pids(arquivo: str):

    df = pd.read_csv(arquivo)

    #converte a coluna code para hexadecimal
    df["code"] = df["code"].apply(lambda x: int(x, 16))

    # Transforma o DataFrame inteiro numa lista de dicionários, um por
    # linha da tabela: [{"code": 12, "name": "rpm", ...}, {...}, ...]
    linhas = df.to_dict("records")

    pids = {}
    for linha in linhas:
    # Cria um Pid de verdade a partir dos dados crus dessa linha.
        pid = Pid(
            code=linha["code"],
            name=linha["name"],
            num_bytes=linha["num_bytes"],
            scale=linha["scale"],
            offset=linha["offset"],
            unit=linha["unit"],
            periodo_ms = linha["periodo_ms"]
        )  
         # Guarda no dicionário final, usando o nome como chave, pra poder chamar pids["rpm"] por exemplo
        pids[linha["name"]] = pid

    return pids;

