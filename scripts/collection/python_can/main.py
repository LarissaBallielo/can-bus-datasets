#TODO COLOCAR IMPORTS NO MAIN
#TODO CRIAR FUNÇÃO carregar_pids
#TODO colocar referencias de funções

import can
from formulasDados import ler_pids
from ObdReader import ObdReader

def main():
    pids = ler_pids("pid.csv") #NOTE oque faz essa função? 
                                 #NOTE era para ser ler_pids de formula dados?
 
    with can.Bus(channel="can0", interface="socketcan") as bus:
        reader = ObdReader(bus, pids) 
        try:
            reader.read_all() # essa função não está sendo chamada
        except KeyboardInterrupt:
            print("Encerrado.")
 
 
if __name__ == "__main__":
    main()