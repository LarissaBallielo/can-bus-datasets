import can
import csv
import pandas as pd

def ler_pids(arquivo: str):
    df = pd.read_csv(arquivo)
    df["PID"] = df["PID"].apply(lambda x: int(x, 16))
    linhas = df.to_dict("records")
    pids = {}

    for linha in linhas:
        pid = Pid(
            code=linha["code"],
            name=linha["name"],
            num_bytes=linha["num_bytes"],
            scale=linha["scale"],
            offset=linha["offset"],
            unit=linha["unit"],
        )
        pids[linha["name"]] = pid #dicionario e a chave é o name

    return pids;

