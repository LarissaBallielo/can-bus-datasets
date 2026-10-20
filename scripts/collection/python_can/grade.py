import pandas as pd, numpy as np

ev = pd.read_csv("eventos.csv")
TOL = {"rpm": 300, "maf": 300, "tps": 500, "engLoad": 500, "velocidade": 500,
+        "stft": 1000, "ltft": 3000, "engCoTemp": 3000, "IAT": 3000, "StsO2Fuel": 3000}

saidas = []
for s, e in ev.groupby("sessao"):
    df = pd.DataFrame({"t_ms": np.arange(0, int(e.t_ms.max()), 100)})
    for pid, g in e.groupby("pid"):
        g = g[["t_ms", "valor"]].rename(columns={"valor": pid}).sort_values("t_ms")
        df = pd.merge_asof(df, g, on="t_ms", direction="backward", tolerance=TOL.get(pid, 500))
    df["sessao"] = s
    saidas.append(df)

grade = pd.concat(saidas, ignore_index=True)
grade.to_csv("dataset_grade.csv", index=False)

# só os trechos válidos para MAF e falsa entrada de ar
valido = grade[(grade.engCoTemp >= 80) & (grade.StsO2Fuel == 512)]
print(len(grade), "linhas na grade;", len(valido), "válidas (quente e malha fechada)")
print("Taxa real por PID (respostas/s):")
print((ev.groupby("pid").size() / (ev.t_ms.max() / 1000)).round(1))