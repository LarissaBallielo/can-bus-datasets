
import time
import can
from formulasDados import ler_pids

'''
manda o pedido de 3 PIDs (RPM, velocidade, MAF) e imprime
a resposta de cada um. 
'''

CHANNEL = "can0" 
PIDS_PARA_TESTAR = ["rpm", "velocidade", "maf"]


def main():
    pids = ler_pids("pid.csv")

    with can.Bus(channel=CHANNEL, interface="socketcan") as bus:
        print("Testando 3 PIDsn")

        for nome in PIDS_PARA_TESTAR:
            pid = pids[nome]

            bus.send(pid.build_request())

            fim = time.time() + 1.0
            valor = None

            while valor is None and time.time() < fim:
                msg = bus.recv(timeout=fim - time.time())
                if msg is None:
                    continue
                valor = pid.decode_response(msg)

            if valor is not None:
                print(f"{pid.name}: {valor:.2f} {pid.unit}")
            else:
                print(f"{pid.name}: sem resposta")


if __name__ == "__main__":
    main()