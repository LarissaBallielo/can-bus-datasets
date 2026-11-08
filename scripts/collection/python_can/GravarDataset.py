import csv
import os
import time

class DataCollect:

    
    def __init__(self, caminho, pids, flag):
        """
        nome:
            Nome do arquivo CSV.

        pids:
            Dicionário de Pid retornado por ler_pids().
        """

        self.caminho = caminho

        # PIDs que são consideraos para leitura,
        # como o Baro é enviado só uma vez ele desconsidera a sua leitura pro buffer

        self.pids = {
            nome: pid
            for nome, pid in pids.items()
            if pid.name != "baro"
        }

        #Set que guarda quais valores já foram recebidos
        self.PIDS_RECEIVED = set()

        #usa na funcao nova
        self.ligado = False
        self.flag = flag
        self.t0 = None
        self.parado_desde = None

        self.partida = 0            # contador de partidas
        self.ultimo_rpm = None      # instante da última resposta de RPM

    def criar_CSV(self) -> None:

        novo = not os.path.exists(self.caminho)

        with open(self.caminho, "a", newline="") as arquivo:
            writer = csv.writer(arquivo)

            if novo:
                writer.writerow(
                     ["t_ms", "pid", "valor", "partida", "flag"] #cabeçalho do formato longo
                )

    def record_reading(self, pid, valor, timestamp) -> None:

        if pid.name not in self.pids:
            return

        self.PIDS_RECEIVED.add(pid.name)

        #faz 3s que nn recebe rpm? chave da ignição desligada 
        if (self.ligado and self.ultimo_rpm is not None and timestamp - self.ultimo_rpm >= 3.0):
            self.ligado = False
            print("Motor desligado (chave desligada).")

        if pid.name == "rpm":
            self.ultimo_rpm = timestamp
            self._estado_motor(valor, timestamp) #manda pro estado motor p saber se o motor está ligado ou desligado.
            if valor > 10000: #leitura invalida
                return

        #so grava com motor ligado
        if not self.ligado:
            return

        # Grava todos os PIDs recebidos, mesmo com o carro parado
        with open(self.caminho, "a", newline="") as arq:
            csv.writer(arq).writerow([ round((timestamp - self.t0) * 1000), pid.name, valor, self.partida, self.flag ])
            arq.flush()

        # Mostra cada leitura no terminal
        print( f"t={round((timestamp - self.t0) * 1000)} ms | " f"PID={pid.name} | valor={valor}", flush=True)


    #timestamp é com base na partida
    def _estado_motor(self, rpm, timestamp):

        if not self.ligado:
            # motor pegou: tempo zera
            if rpm >= 500:      
                self.ligado = True
                self.t0 = timestamp
                self.parado_desde = None
                self.partida +=1
                print(f"Motor ligado. Partida {self.partida}, tempo zerado.")

        #carro morreu, rpm tá 0
        elif rpm < 50:
            if self.parado_desde is None:
                self.parado_desde = timestamp
            #rpm tá abaixo de 50rpm faz 1s -> motor desligado, morreu
            elif timestamp - self.parado_desde >= 1.0:
                self.ligado = False
                print("Motor desligado(morreu)")
        
        #carro ligado, para a contagem
        else:
            self.parado_desde = None 


