


# CAN Bus Datasets — Iniciação Científica

Repositório com os dados e códigos utilizados na Iniciação Científica sobre coleta e análise de dados da rede CAN (Controller Area Network) de veículos, via protocolo OBD-II.

O projeto reúne três origens de dados diferentes:

- **Dados externos**: datasets públicos obtidos na internet;
- **Dados coletados**: dados obtidos diretamente de veículos, via `python-obd` e `python-can`;
- **Dados sintéticos**: dados gerados artificialmente para complementar/testar os modelos.

## Estrutura do repositório
 
```
can-bus-datasets-ic/
├── README.md
├── LICENSE
│
├── data/
│   ├── external/
│   │   └── ved/
│   │       ├── README.md
│   │       ├── LICENSE
│   │       ├── raw/
│   │       └── por_pid/
│   │
│   ├── collected/
│   │   ├── python_obd/
│   │   └── python_can/
│   │
│   └── synthetic/
│       └── README.md
│
├── scripts/
│   ├── collection/
│   │   ├── python_obd/
│   │   └── python_can/
│   ├── synthetic/
│   └── processing/
│
├── docs/
│   └── research-papers-spreadsheet.xlsx
│
└── .gitignore
```
 

## Descrição das pastas

### `data/external/`
Datasets públicos, obtidos prontos na internet (ex.: VED — Vehicle Energy Dataset). Cada dataset externo tem sua própria subpasta com:
- `README.md` próprio, indicando fonte, link original e como citar;
- `LICENSE` original do dataset (preservada, sem se misturar com a licença deste repositório);
- `raw/`: arquivos originais, sem alteração;
- `por_pid/`: dados separados por PID individual, conforme os PIDs escolhidos para análise no momento.

### `data/collected/`
Dados coletados diretamente de veículos pelo grupo de pesquisa.
- `python_obd/`: dados coletados usando a biblioteca [python-OBD](https://github.com/brendan-w/python-OBD), que já decodifica os PIDs.
- `python_can/`: dados coletados usando a biblioteca [python-can](https://python-can.readthedocs.io/), com os frames CAN mais crus, sem decodificação de PID.

### `data/synthetic/`
Dados gerados sinteticamente pelo grupo, com README explicando o método usado para geração.

### `scripts/`
Todo o código do projeto, separado por finalidade:
- `collection/python_obd/` e `collection/python_can/`: scripts de coleta correspondentes a cada biblioteca;
- `synthetic/`: scripts usados para gerar os dados sintéticos;
- `processing/`: scripts de leitura, tratamento e análise dos dados (ex.: `lerArquivo.py`).

### `docs/`
Material de apoio da IC, como a planilha de levantamento de artigos/referências.
