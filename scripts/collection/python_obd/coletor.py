import csv
import obd
import os

from RASP import RASPstrategy
from constants import(
    NOME,
    HEADER,
)


class DataCollect(RASPstrategy):

    def __init__(self) -> None:
        self.connection = None
        self.MSG_BUFFER = [0 ,0, 0]
        self.RPM_RECIEVED = False
        self.MAF_RECIEVED = False
        self.LTFT_RECIEVED = False


    @staticmethod
    def criar_CSV(nome, header) -> None:
        """
            creates the CSV, and if its first instance it markes
            first row with only headers
        """
        novo  = not os.path.exists(nome)
        with open(nome, "a", newline="") as arquivo: # uando terminar o bloco, ele fecha o arquivo automaticamente.
            writer = csv.writer(arquivo)

            if novo:
                writer.writerow(header)

    def RPM_callback(self, r) -> None:

        self.MSG_BUFFER[0] = r.value
        self.RPM_RECIEVED = True
        self._BUFFER_CHECK()
        


    def LTFT_callback(self, l) -> None:

        self.MSG_BUFFER[1] = l.value
        self.LTFT_RECIEVED = True
        self._BUFFER_CHECK()

    def MAF_callback(self, m) -> None:

        self.MSG_BUFFER[2] = m.value
        self.MAF_RECIEVED = True
        self._BUFFER_CHECK()

    def _BUFFER_CHECK(self) -> bool: 
        """
            WAITS FOR ALL THE MESSAGES TO BE SENT
        """

        
        if self.RPM_RECIEVED and self.MAF_RECIEVED and self.LTFT_RECIEVED:
            with open(NOME, "a", newline="") as arquivo:
                writer = csv.writer(arquivo)
                writer.writerow(self.MSG_BUFFER)
            self.RPM_RECIEVED = False
            self.MAF_RECIEVED = False
            self.LTFT_RECIEVED = False
            return True
        
        return False        


    def run(self) -> None:
        try:
            self.criar_CSV(NOME, HEADER)
            self.connection = obd.Async()


            self.connection.watch(obd.commands.RPM, callback=self.RPM_callback)
            self.connection.watch(obd.commands.MAF, callback=self.MAF_callback)
            self.connection.watch(obd.commands.LONG_FUEL_TRIM_1, callback=self.LTFT_callback) #NOTE aqui devemos analisar caso de dois bancos de cilindros

            self.connection.start() # cria uma nova thread
        except KeyboardInterrupt:
            print("KEYBOARD INTERRUPT, finalizing collection stage")
            self.connection.stop()



