#TODO COLOCAR IMPORTS NO MAIN
#TODO CRIAR FUNÇÃO carregar_pids
#TODO colocar referencias de funções

import can
from formulasDados import ler_pids
from ObdReader import ObdReader

def main():
    pids = ler_pids("pid.csv")  
 
    with can.Bus(channel="can0", interface="socketcan") as bus:
        reader = ObdReader(bus, pids) 
        try:
            reader.read_all() 
        except KeyboardInterrupt:
            print("Encerrado.")
 
 
if __name__ == "__main__":
    main()