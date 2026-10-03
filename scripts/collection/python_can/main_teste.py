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

    # Cria o objeto responsável pelo CSV
    coletor = DataCollect(
        "/home/canlab/can-bus-datasets/data/dataset.csv",
        pids,
        pids_ancora
    )

    # Cria o arquivo e o cabeçalho caso necessário
    coletor.criar_CSV()

    with can.Bus( channel="can0", interface="socketcan" ) as bus:

        reader = ObdReader(bus,pids)

        try:
            # Passa a função do DataCollect como callback.
            reader.read_all( funcao=coletor.receber_dado)

        except KeyboardInterrupt:
            print("Encerrado.")


if __name__ == "__main__":
    main()