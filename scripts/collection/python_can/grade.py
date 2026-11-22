import pandas as pd, numpy as np

nome_arq = input("nome do arquivo: ")

fast = ["velocidade", "maf", "rpm", "tps", "stft"]                     # até 200 ms
medium  = ["ltft", "engCoTemp", "O2_B1S1_tensao", "TPScom", "StsO2Fuel",
           "Pedal", "Purga", "Lambda_comandada"]                          # 0,5 a 1 s
slow  = ["Etanol", "IAT"]                                               # 5 s


FEATURES = {
    "media":    ["trim_total", "stft", "maf_rpm", "TPScom",
                 "rpm", "velocidade", "engCoTemp", "Etanol"],
    "dp":       ["rpm"],
    "max":      ["rpm", "tps", "maf", "velocidade", "stft"],
    "derivada": ["velocidade", "tps", "maf"],
    "integral": [],
}

COLUNAS_CALCULADAS = {
    "trim_total": lambda g: g["stft"] + g["ltft"],
    "maf_rpm":    lambda g: g["maf"] / g["rpm"],
    "maf_esperado": lambda g: 7.77
}

STATS_DERIVADA = ["media", "max", "min"]

caminho = "/home/larissa/Documents/UNIFEI/IC/can-bus-datasets/data/collected/" + nome_arq + ".csv"
df = pd.read_csv(caminho)

flag = df["flag"].iloc[0]   

linhas = []

#agrupa por partida, primeiro cria linhas de 1s
for partida, df_p in df.groupby("partida"):

    #separa por segundo
    df_p = df_p.copy()
    df_p["seg"] = df_p["t_ms"]//1000       # 2
    grade = df_p.pivot_table(
        index="seg",
        columns=["pid"],
        values="valor",
        aggfunc="mean"
    )

    #preenche os espaços vazios
    s = [c for c in slow if c in grade]
    grade[s] = grade[s].ffill(limit=8)
    grade[medium]  = grade[medium].ffill(limit=3)
    grade[fast] = grade[fast].ffill(limit=2)
    

    #cria colunas trim_total, maf_rpm e maf_esperado
    for nome, funcao in COLUNAS_CALCULADAS.items():
        grade[nome] = funcao(grade)

    #preenche as que estão sem dados com NaN
    grade = grade.reindex(range(grade.index.max() + 1))

    #cria a coluna janela
    grade["janela"] = grade.index // 30

    for n_janela, conteudo in grade.groupby("janela"):
        cobertura = conteudo["rpm"].notna().sum() / 30
        if cobertura < 0.8:
            continue

        linha = {
            "partida":   partida,
            "janela":    n_janela,
            "flag": flag}

        # médias
        for pid in FEATURES["media"]:
            linha[f"{pid}_media"] = conteudo[pid].mean()

        # desvio padrão
        for pid in FEATURES["dp"]:
            linha[f"{pid}_dp"] = conteudo[pid].std()

        # máximos
        for pid in FEATURES["max"]:
            linha[f"{pid}_max"] = conteudo[pid].max()

        #derivada
        for pid in FEATURES["derivada"]:
            valores = conteudo[pid]
            if pid == "velocidade":
                valores = valores / 3.6          # km/h -> m/s (aceleração em m/s²)
            deriv = valores.diff()               # calcula a derivada pra cada linha
            linha[f"d{pid}_media"] = deriv.mean()
            linha[f"d{pid}_max"]   = deriv.max()
            linha[f"d{pid}_min"]   = deriv.min()

        linhas.append(linha)

    print(grade.head(8))

    grade.to_csv("/home/larissa/Documents/UNIFEI/IC/can-bus-datasets/data/collected/arq_teste.csv",index=False)
