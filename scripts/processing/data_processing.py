from pathlib import Path

import csv
import numpy as np


class PID_LIST:

    def __init__(self, data, intervalo = 30):
        """
        função de abstração para criação de um dataset ordenado por timestamps e com tratamento de dados,
        inicialize o objeto sempre com o csv já lido pelo reader como parametro.
        """
        
        
        self.MAF: list[float] = []
        self.MAP: list[float] = []
        self.VELOCIDADE: list[float] = []
        self.RPM: list[float] = []
        self.TPS: list[float] = []
        self.LTFT: list[float] = []
        self.STFT: list[float] = []
        self.ENGCOTEMP: list[float] = []
        self.FUELP: list[float] = []
        self.ENGLOAD: list[float] = []

        self.intervalo = intervalo
        self.divisor = 1000
        self.dataset = data

    @staticmethod
    def _dividir_dataset(leitor, intervalo=5,
                         timestamp_col="timestamp", divisor=1000):

        inicio_dataset = None
        indice_janela_atual = None
        linhas_janela = []
        ultimo_timestamp = None

        for linha in leitor:
            timestamp = float(linha[timestamp_col]) / divisor

            if inicio_dataset is None:
                inicio_dataset = timestamp

            if ultimo_timestamp is not None and timestamp < ultimo_timestamp:
                raise ValueError("Dataset precisa estar ordenado.")

            indice_janela = int((timestamp - inicio_dataset) // intervalo)

            if indice_janela_atual is None:
                indice_janela_atual = indice_janela

            if indice_janela != indice_janela_atual:

                yield {
                    "inicio": inicio_dataset + indice_janela_atual * intervalo,
                    "fim": inicio_dataset + (indice_janela_atual + 1) * intervalo,
                    "linhas": linhas_janela
                }

                linhas_janela = []
                indice_janela_atual = indice_janela

            linhas_janela.append(linha)
            ultimo_timestamp = timestamp

        if linhas_janela:
            yield {
                "inicio": inicio_dataset + indice_janela_atual * intervalo,
                "fim": inicio_dataset + (indice_janela_atual + 1) * intervalo,
                "linhas": linhas_janela
            }

    def _parse_to_list(self, linhas):

        # Limpa os dados da janela anterior
        for pid, value in vars(self).items():
            if isinstance(value, list):
                value.clear()

        for linha in linhas:

            self.MAF.append(float(linha["maf"]))
            self.MAP.append(float(linha["map"]))
            self.VELOCIDADE.append(float(linha["velocidade"]))
            self.RPM.append(float(linha["rpm"]))
            self.TPS.append(float(linha["tps"]))
            self.LTFT.append(float(linha["ltft"]))
            self.STFT.append(float(linha["stft"]))
            self.ENGCOTEMP.append(float(linha["engCoTemp"]))
            self.FUELP.append(float(linha["fuelP"]))
            self.ENGLOAD.append(float(linha["engLoad"]))

    def meas(self) -> list[dict]:
        """
        Cria a partir de dataset csv ORDENADO POR TIMESTAMP, um dataset baseado em windows, EXEMPLO ->
        
            with open("~/PROJECTS/IC/can-bus-datasets/data/dataset.csv", mode="r", encoding="utf-8", newline="") as arquivo:
            
                leitor = csv.DictReader(arquivo)
                machine = PID_LIST(leitor)
                resultado = machine.meas()        
        
        """
        
        _final_list = []

        for window in self._dividir_dataset(
            self.dataset,
            intervalo=self.intervalo,
            divisor=self.divisor
        ):

            # Converte as linhas da janela em listas de PIDs
            self._parse_to_list(window["linhas"])

            # Um dicionário de features por janela
            _line_dict = {
                "inicio": window["inicio"],
                "fim": window["fim"]
            }

            for pid, value in vars(self).items():

                if isinstance(value, list) and len(value) > 0:

                    media = np.mean(value)
                    desvio = np.std(value)
                    maximo = np.max(value)
                    minimo = np.min(value)

                    # Proporção de amostras disponíveis
                    valid_ratio = len(value) / len(window["linhas"])

                    _line_dict[f"{pid}_mean"] = media
                    _line_dict[f"{pid}_std"] = desvio
                    _line_dict[f"{pid}_max"] = maximo
                    _line_dict[f"{pid}_min"] = minimo
                    _line_dict[f"{pid}_ratio"] = valid_ratio

            _final_list.append(_line_dict)

        return _final_list
    
    @staticmethod    
    def resolve_csv(result: list[dict], path: str) -> None:
        """
        função cria o csv a partir do resultado obtido de meas, demonstração->
            
            with open("~/PROJECTS/IC/can-bus-datasets/data/dataset.csv", mode="r", encoding="utf-8", newline="") as arquivo:
            
                leitor = csv.DictReader(arquivo)
                machine = PID_LIST(leitor)
                resultado = machine.meas()
                machine.resolve_csv(result = resultado, path = "~/PROJECTS/IC/can-bus-datasets/data")        
        """
        
        if not result:
            raise ValueError("Ta vazio o result")

        fieldnames = result[0].keys()

        with open(path, mode="w", encoding="utf-8", newline="") as arquivo:

            escritor = csv.DictWriter(arquivo, fieldnames=fieldnames)

            escritor.writeheader()
            escritor.writerows(result)


def main() -> None:
    
    PROJECT_ROOT = Path(__file__).resolve().parents[2]

    DATASET_PATH = PROJECT_ROOT / "data" / "dataset.csv"
    WINDOED_PATH = PROJECT_ROOT / "data" / "windoed.csv"
    with open(DATASET_PATH, mode="r", encoding="utf-8", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        machine = PID_LIST(leitor, 0.5)
        resultado = machine.meas()
        machine.resolve_csv(result = resultado, path = WINDOED_PATH)        

if __name__ == "__main__":
    main()