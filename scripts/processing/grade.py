import pandas as pd, numpy as np


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



def montar_grade(df_p):
    """
    Recebe as leituras por partida e devolve uma tabela com uma linha por seg
    longo -> largo
    """
    #separa por segundo
    df_p["seg"] = df_p["t_ms"]//1000       # 2
    grade = df_p.pivot_table(
        index="seg",
        columns=["pid"],
        values="valor",
        aggfunc="mean"
    )


    #preenche as que estão sem dados com NaN
    grade = grade.reindex(range(grade.index.max() + 1))

    #preenche os espaços vazios o s, m e f é pra conferir se os pids existem naquele carro
    s = [c for c in slow if c in grade]
    grade[s] = grade[s].ffill(limit=8)
    m = [c for c in medium if c in grade]
    grade[m]  = grade[m].ffill(limit=3)
    f = [c for c in fast if c in grade]
    grade[f] = grade[f].ffill(limit=2)
    

    #cria colunas trim_total, maf_rpm e maf_esperado
    for nome, funcao in COLUNAS_CALCULADAS.items():
        grade[nome] = funcao(grade)

    #cria a coluna janela
    grade["janela"] = grade.index // 30

    return grade



def calcular_features(conteudo):
    """
    recebe os segundos de uma janela e devolve a linha/janela de 30s q é um dicionario
    """

    linha = {}

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
    
    return linha






nome_arq = input("nome do arquivo: ")

caminho = "/home/larissa/Documents/UNIFEI/IC/can-bus-datasets/data/collected/" + nome_arq + ".csv"
df = pd.read_csv(caminho)

flag = df["flag"].iloc[0]   

linhas = []

#agrupa por partida, primeiro cria linhas de 1s
for partida, df_p in df.groupby("partida"):
    df_p = df_p.copy() 
    grade = montar_grade(df_p)
    
    for n_janela, conteudo in grade.groupby("janela"):
        cobertura = conteudo["rpm"].notna().sum() / 30
        if cobertura < 0.8:
            continue
        linha = {"partida": partida, "flag": flag}   
        linha.update(calcular_features(conteudo))                       # acrescenta as chaves da funcao no dict linha
        linhas.append(linha)

    #linhas e uma lista de dicionarios
resultado = pd.DataFrame(linhas)
resultado = resultado.round(2)          
caminho_salvar = "/home/larissa/Documents/UNIFEI/IC/can-bus-datasets/data/collected/" + nome_arq + "_j.csv"
resultado.to_csv(caminho_salvar,index=False)



