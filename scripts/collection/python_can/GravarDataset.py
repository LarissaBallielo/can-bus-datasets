import csv
import os


class DataCollect:

    def __init__(self, nome, pids, pids_ancora):
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

        self.pids_ancora = set(pids_ancora) #pids que vai de 50 em 50ms
        self.recebidos_ancora = set()

        self.pronto = False #ja coletou a primeira linha? 1x cada dado?

    def criar_CSV(self) -> None:

        novo = not os.path.exists(self.nome)

        with open(self.nome, "a", newline="") as arquivo:
            writer = csv.writer(arquivo)

            if novo:
                writer.writerow(
                    list(self.pids.keys()) + ["timestamp"] #escreve o cabeçalho se for novo
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

        if(not self.pronto): self._BUFFER_CHECK()
        '''
        Ao inves de chamar o buffer check toda vaz, que grava o timestamp com base na resposta mais demorada, chama ele apenas na primeira vez
        pra ter um valor de cada PID

        '''
        else: self.gravar_dados(pid, valor, timestamp)

    def gravar_linha(self):
        linha = []

        for nome in self.pids.keys():
            linha.append(self.MSG_BUFFER[nome])

        linha.append(self.TIMESTAMP)

        with open(self.nome, "a", newline="") as arquivo:
            writer = csv.writer(arquivo)
            writer.writerow(linha)
            print(f"LINHA adicionada: {linha}")


    def gravar_dados(self, pid, valor, timestamp):
        '''
        toda vez q recebo um dado, escrevo ele no buffer, mas antes de gravar uma linha, espera os dados que são de 50 em 50ms pra gravar
        '''
        
        self.MSG_BUFFER[pid.name] = valor   # sempre atualiza, igual já fazia
        self.TIMESTAMP = timestamp

        if pid.name in self.pids_ancora:
            self.recebidos_ancora.add(pid.name)

        if self.recebidos_ancora == self.pids_ancora:
        self.gravar_linha()
        self.recebidos_ancora.clear()   # só limpa ESSE conjunto, não o MSG_BUFFER


        
    def _BUFFER_CHECK(self) -> bool:
        """
        essa função vai checar o buffer de mensagem e ver se ele já está completo
        """

        if self.PIDS_RECEIVED != set(self.pids.keys()):
            return False

        self.gravar_linha()

        # self.MSG_BUFFER.clear() não precisa limpar pois quando chegar um valor novo será sobrescrito
        # self.PIDS_RECEIVED.clear() nao vai usar dnv
        # self.TIMESTAMP = None nao precisa limpar pq vai ser sobrescrito

        return True

