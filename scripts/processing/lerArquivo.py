
import pandas as pd
import glob

# Carrega o excel
df = pd.read_excel("/home/larissa/Documents/UNIFEI/IC/Dataset_internet/Data/VED_Static_Data_ICE&HEV.xlsx")

# 1. Filtrar por palavra-chave em uma coluna (mantém só as linhas que contêm a palavra)
palavra_chave = "ICE"
df_filtrado = df[df["Vehicle Type"].str.contains(palavra_chave, case=False, na=False)]

# 2. Excluir linhas com base em valores de outra coluna
valores_para_excluir = "DSL"
df_final = df_filtrado[~df_filtrado["Engine Configuration & Displacement"].str.contains(valores_para_excluir, case=False, na=False)]

# Salva o resultado em um novo CSV (ou sobrescreve o original)
df_final.to_csv("carros_usados.csv", index=False)


#arquivos csv
valores_carros = df_final["VehId"]

arquivos = glob.glob("/home/larissa/Documents/UNIFEI/IC/Dataset_internet/Data/dados/*.csv")

df_dados = pd.concat(
    [pd.read_csv(arquivo) for arquivo in arquivos],
    ignore_index=True
)

pids_usados = ["MAF[g/sec]", "Engine RPM[RPM]", "Vehicle Speed[km/h]", "Absolute Load[%]", "Short Term Fuel Trim Bank 1[%]", "Long Term Fuel Trim Bank 1[%]"]

df_dados = df_dados[(df_dados["VehId"].isin(valores_carros))&
                    (~df_dados[pids_usados].isna().any(axis=1))] #.any(axis=1) -> pelo menos 1

df_dados.drop(['OAT[DegC]','Fuel Rate[L/hr]','Air Conditioning Power[kW]','Air Conditioning Power[Watts]',
             'Heater Power[Watts]','HV Battery Current[A]','HV Battery SOC[%]','HV Battery Voltage[V]'],
             axis=1, inplace=True)

df_dados.to_csv("dataset.csv", index=False)