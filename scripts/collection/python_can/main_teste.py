import can

from formulasDados import ler_pids
from ObdReader import ObdReader
from GravarDataset import DataCollect


def main():

    # Carrega os PIDs do pid.csv
    pids = ler_pids("pid.csv")

    # Cria o objeto responsável pelo CSV
    coletor = DataCollect(
        "dataset.csv",
        pids
    )

    # Cria o arquivo e o cabeçalho caso necessário
    coletor.criar_CSV()

    with can.Bus(
        channel="can0",
        interface="socketcan"
    ) as bus:

        reader = ObdReader(
            bus,
            pids
        )

        try:
            # Passa a função do DataCollect como callback.
            reader.read_all(
                funcao=coletor.receber_dado
            )

        except KeyboardInterrupt:
            print("Encerrado.")


if __name__ == "__main__":
    main()