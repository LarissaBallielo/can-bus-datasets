import csv
import os


class DataCollect:

    def __init__(self, nome, pids):
        """
        nome:
            Nome do arquivo CSV.

        pids:
            Dicionário de Pid retornado por ler_pids().
        """

        self.nome = nome

        # PIDs que são consideraos para leitura,
        # como o Baro é enviado só uma vez ele desconsidera a sua leitura pro buffer

        self.pids = {
            nome: pid
            for nome, pid in pids.items()
            if pid.name != "baro"
        }

        # Dicionário que guarda os valores recebidos
        self.MSG_BUFFER = {}

        self.TIMESTAMP = None

        #Set que guarda quais valores já foram recebidos
        self.PIDS_RECEIVED = set()

    def criar_CSV(self) -> None:

        novo = not os.path.exists(self.nome)

        with open(self.nome, "a", newline="") as arquivo:
            writer = csv.writer(arquivo)

            if novo:
                writer.writerow(
                    list(self.pids.keys()) + ["timestamp"]
                )

    def receber_dado(self, pid, valor, timestamp) -> None:
        """
        essencialmente a função callback de obdReader que recebe dados lidos por ela
        """

        # Verifica se o PID não faz parte do dataset
        if pid.name not in self.pids:
            return

        self.MSG_BUFFER[pid.name] = valor

        print(f"RECEBIDO: {pid.name} = {valor} | buffer: {len(self.PIDS_RECEIVED)} / {len(self.pids)}")

        # Marca esse PID como recebido para a amostra atual.
        self.PIDS_RECEIVED.add(pid.name)

        self.TIMESTAMP = timestamp

        self._BUFFER_CHECK()

    def _BUFFER_CHECK(self) -> bool:
        """
        essa função vai checar o buffer de mensagem e ver se ele já está completo
        """

        if self.PIDS_RECEIVED != set(self.pids.keys()):
            return False

        linha = []

        for nome in self.pids.keys():
            linha.append(self.MSG_BUFFER[nome])

        linha.append(self.TIMESTAMP)

        with open(self.nome, "a", newline="") as arquivo:
            writer = csv.writer(arquivo)
            writer.writerow(linha)
            print(f"LINHA adicionada: {linha}")

        self.MSG_BUFFER.clear()
        self.PIDS_RECEIVED.clear()
        self.TIMESTAMP = None

        return True

