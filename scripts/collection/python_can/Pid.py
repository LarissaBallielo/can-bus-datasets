import time 
import can

class Pid:
    def __init__(self, code, name, formula):
        self.code = code
        self.name = nome
        self.num_bytes = num_bytes
        self.scale = scale
        self.offset = offset
        self.unit = unit
        self.periodo_ms
        self.listaIds = [0x7E8, 0x7E9, 0x7EA, 0x7EB, 0x7EC, 0x7ED, 0x7EE, 0x7EF] #lista de IDs de possiveis respostas ao OBD2, variam conforme a ECU


    def formula(self, msg: Message):
        for i in range(self.num_bytes):
            valor = msg.data[3+i]
        return valor*self.scale + self.offset 

    #monta e devolve a mensagem do pedido
    def build_request(self):
        msg = can.Message(arbitration_id=0x7DF, data=[0x02, 0x01, code, 0x00, 0x00, 0x00, 0x00, 0x00], is_extended_id=False)
        return msg

    #verifica primeiro se é uma resposta ao obd2(pelo ID) e 
    #se é do PID certo, aí pega os dados
    def decode_response(self, msg:Message):
        resposta = False
        if len(msg.data) < 3: return None
        for id in self.listaIds :
            if (msg.arbitration_id == id):
                resposta = True
        if not (msg.data[1] == 0x41): return None
        if resposta == False : return None
        if msg.data[2] != self.code:
            return None

        return self.formula(msg.data[3:])

