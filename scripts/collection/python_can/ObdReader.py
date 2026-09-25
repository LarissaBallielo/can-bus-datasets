import time 
import can
from pid import Pid

"""
ObdReader: orquestra a leitura dos PIDs do OBD2, usando um bus (conexão
CAN já aberta) e uma coleção de Pids
 
- read_pid_only(): lê um PID isolado, uma vez, de forma síncrona --
    bom pra debugar um PID específico, ou pra ler algo que só precisa ser
    pedido uma vez (ex: pressão barométrica).
- start()/escutar()/stop() (e o read_all()): pedem todos os PIDs da lista
    (que são os que vamos usar na falha do MAF)
    continuamente, cada um na sua própria frequência, em segundo plano.
"""

class ObdReader :
    def __init__(self, bus, pids):
        self.bus = bus
        self.pids = pids
        self.pids_por_code = {pid.code: pid for pid in pids.values()}
        self._tasks = []

    def read_pid_only(self, pid: Pid, timeout: float=1.0, funcao=print):
        '''
        manda o pedido, espera a resposta certa chegar, ignorando qualquer outra coisa que aparecer
        no barramento, bloqueante
        parametros:
        timeout: por quantos segundos no máximo vale a pena esperar antes de desistir
        funcao: o que fazer com o resultado, se chegar uma resposta válida
        '''
        #solicita o dado
        msg = pid.build_request()
        self.bus.send(msg)
        
        fim = time.time() +timeout
        dado = None
        mensagem =  None
        
        while dado is None and time.time() <fim:
            mensagem = self.bus.recv(timeout=fim - time.time()) #tempo que sobra
            if mensagem is None: continue
            dado = pid.decode_response(mensagem)  # se dado continuar None aqui, era resposta de outra coisa
        
        if dado is not None: funcao(dado, mensagem.timestamp)

    def start(self):
        '''
        Começa a reenviar o pedido de cada PID sozinho, cada um na sua frequência
        le primeiro a pressão barométrica, uma vez apenas
        Guarda cada "tarefa" que send_periodic() devolve em self._tasks,
        pra poder desligar todas elas depois, em stop().
        '''
        self.read_pid_only(self.pids["baro"])

        for pid in self.pids.values():
            if pid.name == "baro": continue # pula o barometro q ja foi lido
            msg = pid.build_request()
            periodo_segundos = pid.periodo_ms / 1000
            task = self.bus.send_periodic(msg, periodo_segundos)
            self._tasks.append(task)

    def stop(self):
        '''
        Para todos os envios periódicos que start_periodic() começou
        chamando .stop() em cada "tarefa" guardada em self._tasks. Depois, limpa a
        lista 
        '''
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

        parametros:
        duracao_segundos : por quanto tempo continuar escutando
        funcao: o que fazer pra cada resposta valida que chegar
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

    def read_all(self, duracao_segundos=None, funcao=print):
        '''
        junta o ciclo completo numa chamada ,  começa os envios
        periódicos (start), escuta as respostas (escutar), e garante que os
        envios periódicos param no final (stop)
        '''
        self.start()
        try:
            self.escutar(duracao_segundos=duracao_segundos, funcao=funcao)
        finally:
            self.stop()
