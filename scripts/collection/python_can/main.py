#TODO COLOCAR IMPORTS NO MAIN
#TODO CRIAR FUNÇÃO carregar_pids
#TODO colocar referencias de funções

import can
from .formulasDados import ler_pids

def main():
    pids = criar_csv("pids.csv") #NOTE oque faz essa função? 
                                 #NOTE era para ser ler_pids de formula dados?
 
    with can.Bus(channel="can0", interface="socketcan") as bus:
        reader = ObdReader(bus, pids) 
        try:
            read_all() # essa função não está sendo chamada
        except KeyboardInterrupt:
            print("Encerrado.")
 
 
if __name__ == "__main__":
    main()