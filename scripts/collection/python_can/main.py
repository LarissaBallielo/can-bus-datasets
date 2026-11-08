import can

from formulasDados import ler_pids
from ObdReader import ObdReader
from GravarDataset import DataCollect


def main():

    # Carrega os PIDs do pid.csv em um dicionario
    pids = ler_pids("pid.csv")
    pids_ancora = set()

    #vê os PIDs que tem o periodo de 50ms e põe na lista pids_ancora
    for pid in pids.values():
        if(pid.periodo_ms == 50):
            pids_ancora.add(pid.name)

    #nome arquivo (carro_data_flag)
    nome = input("carro: ")
    data = input("data: ")
    flag = input("flag(0-sem falha/1-com falha): ")

    caminho = f"/home/canlab/can-bus-datasets/data/collected/{nome}_{data}_{flag}"

    # Cria o objeto responsável pelo CSV
    coletor = DataCollect( caminho, pids, flag )


    # Cria o arquivo e o cabeçalho caso necessário
    coletor.criar_CSV()


    #can0 para mcp2515 e can1 para canable
    with can.Bus( channel="can0", interface="socketcan" ) as bus:

        reader = ObdReader(bus,pids)

        try:
            # Passa a função do DataCollect como callback.
            reader.read_all( funcao=coletor.record_reading)

        except KeyboardInterrupt:
            print("Encerrado.")
            print("Nunca responderam:", set(coletor.pids) - coletor.PIDS_RECEIVED)

if __name__ == "__main__":
    main()