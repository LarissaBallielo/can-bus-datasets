import time 
import can
from pid import Pid

class ObdReader :
    def __init__(self, bus, pids):
        self.bus = bus
        self.pids = pids
        self.pids_por_code = {pid.code: pid for pid in pids.values()}
        self._tasks = []

    def read_pid_only(self,pid: Pid, timeout: float=1.0, funcao=print):

        msg = pid.build_request()
        self.bus.send(msg)
        
        fim = time.time() +timeout
        dado = None
        
        while dado is None and time.time() <fim:
            mensagem = self.bus.recv(timeout=timeout)
            if mensagem is None: continue
            dado = pid.decode_response(mensagem)
        
        funcao(dado, mensagem.timestamp)

    def start(self):
         #Começa a reenviar o pedido de cada PID sozinho, cada um na sua frequência
        read_pid_only(self.pids["baro"])
        for pid in self.pids:
            msg = pid.build_request()
            periodo_segundos = pid.period_ms / 1000
            task = self.bus.send_periodic(msg, periodo_segundos)
            self._tasks.append(task)

    def stop(self):
        #Para todos os envios periódicos que start_periodic() começou
        for task in self._tasks:
            task.stop()
        self._tasks = []

    def escutar(self, duracao_segundos = None, funcao = print): #funcao q vai ser executada 
        """
        Fica recebendo as respostas continuamente. 
        
        Pra cada resposta válida,
        descobre a qual Pid ela pertence e chama uma guncao, que vai ser gravar_arquivo
 
        Se duracao_segundos for None, roda pra sempre (até Ctrl+C ou até
        ser interrompido de outra forma).
        """

        #calcula o tempo que deve parar
        fim = time.time() + duracao_segundos if duracao_segundos else None
 
        while fim is None or time.time() < fim:
            msg = self.bus.recv(timeout=0.5)
            if msg is None:
                continue
 
            if len(msg.data) < 3:
                continue  # frame curto demais pra ter PID ecoado
 
            pid_code = msg.data[2]
            pid = self.pids_por_code.get(pid_code)
            if pid is None:
                continue  # resposta de um PID que não estamos monitorando
 
            valor = pid.decode_response(msg)
            if valor is not None:
                funcao(pid, valor, msg.timestamp)

    def read_all(self, duracao_segundos=None, ao_receber=print):
        self.start()
        try:
            self.escutar(duracao_segundos=duracao_segundos, funcao=funcao)
        finally:
            self.stop()
