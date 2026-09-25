import time 
import can
from can import Message

"""
Classe Pid: representa um único parâmetro do OBD2 (RPM, MAF, velocidade...).
 
Cada instância sabe, sozinha: como montar o pedido daquele parâmetro, e como
decodificar a resposta que o carro devolve, sem que o resto do código
(ObdReader) precise saber nada sobre o formato dos bytes.
"""

class Pid:
    def __init__(self, code, name, num_bytes, scale, offset, unit, periodo_ms, formula): # está passando muito pouco argumentos vai dar erro
        self.code = code # código do PID em hexadecimal
        self.name = name
        self.num_bytes = num_bytes #quantos bytes de dado a resposta desse PID traz
        self.scale = scale  # multiplicador aplicado no valor bruto
        self.offset = offset # valor somado depois da escala
        self.unit = unit # unidade(km/h, s, rpm..)
        self.periodo_ms = periodo_ms # tempo em milissegundos o qual esse PID deve ser solicitado de novo (frequencia)
        self.listaIds = [0x7E8, 0x7E9, 0x7EA, 0x7EB, 0x7EC, 0x7ED, 0x7EE, 0x7EF] #lista de IDs de possiveis respostas ao OBD2, variam conforme a ECU

    
    #Pega os bytes de dado da resposta e transforma no valor real
    def formula(self, dados):
        '''
        Recebe só os bytes de dado já extraídos da resposta, combina eles em um unico valor inteiro
        e depois aplica a formula linear da norma SAE J1979 
        '''
        valor = 0
        for i in range(self.num_bytes):
            valor = valor * 256 + dados[i]        
        return valor*self.scale + self.offset 

    def build_request(self):
         """
        Monta e devolve o frame de pedido do OBD2 (modo 01 = "leitura de
        dado atual") pra este PID específico. 
        Formato do pedido (sempre 8 bytes, sempre pro ID 0x7DF = broadcast):
            byte 0: 0x02  -> avisa que só os 2 próximos bytes são úteis
            byte 1: 0x01  -> modo 01 (leitura de dado atual)
            byte 2: code  -> o PID que estamos pedindo
            bytes 3-7: 0x00 (padding, sem uso)
        """
        msg = can.Message(arbitration_id=0x7DF, data=[0x02, 0x01, self.code, 0x00, 0x00, 0x00, 0x00, 0x00], is_extended_id=False)
        return msg

    #verifica primeiro se é uma resposta ao obd2(pelo ID) e 
    #se é do PID certo, aí pega os dados
    def decode_response(self, msg:Message):
         """
        Confere se msg é uma resposta válida a este PID, e se for, devolve
        o valor já decodificado (float). Devolve None em qualquer caso de
        falha
        """
        resposta = False

        #mensagens com menos de 3 bytes : inválidas, só ruído
        if len(msg.data) < 3: return None

        #confirma que a mensagem veio de um dos IDs de resposta do OBD2
        for id in self.listaIds :
            if (msg.arbitration_id == id):
                resposta = True
        if resposta == False : return None

        #confirma que é uma resposta ao modo 01 (0x41 = 0x01 + 0x40)
        if not (msg.data[1] == 0x41): return None

        #confirma que é resposta a esse PID específico
        if msg.data[2] != self.code:
            return None

        return self.formula(msg.data[3:])

