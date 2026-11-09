# Associação de IDs Nox a referências próximas

Este projeto relaciona cada **ID Nox** à referência geográfica mais próxima, como um ponto de infraestrutura, estacionamento ou outro elemento cadastrado. O resultado é exportado como um arquivo CSV com o ID, o tipo e o nome da referência encontrada, além da distância em metros.

## Privacidade e dados ocultados

Este repositório foi preparado para ser compartilhado sem revelar informações pessoais, institucionais ou operacionais que não são necessárias para compreender ou executar o algoritmo.

Foram ocultados ou generalizados:

- O caminho local completo dos dados, que continha nome de usuário, serviço de armazenamento, curso e contexto do projeto.
- Os nomes originais dos arquivos de entrada e saída, substituídos por nomes neutros como `referencias.csv`, `luminarias.csv` e `resultado.csv`.
- A localização física dos arquivos no computador. Ela é informada em tempo de execução pela variável de ambiente `NOX_DADOS_DIR`.
- Mensagens de erro que poderiam revelar a estrutura interna das tabelas, como a lista completa de colunas disponíveis.

O arquivo `referencias.csv` pode ser incluído no repositório, pois suas referências estão autorizadas para disponibilização. Já o arquivo `luminarias.csv` não deve ser publicado sem uma revisão específica, pois pode conter identificadores, coordenadas ou leituras operacionais que exijam proteção.

## Como o código funciona

1. O programa lê dois arquivos CSV:
   - `referencias.csv`: contém os pontos de referência, seus tipos, nomes e coordenadas.
   - `luminarias.csv`: contém os IDs Nox e as coordenadas das luminárias.

2. Os cabeçalhos são normalizados para tolerar diferenças de maiúsculas, acentos e espaços. Por exemplo, `Latitude`, `latitude` e `LATITUDE` são tratados de maneira equivalente.

3. As coordenadas são convertidas para números, aceitando valores com vírgula ou ponto decimal. Linhas com coordenadas inválidas — incluindo a coordenada nula `(0, 0)` para luminárias — não recebem uma referência próxima.

4. Caso existam várias leituras para o mesmo ID Nox, apenas a primeira é mantida, pois as coordenadas são consideradas iguais para aquele identificador.

5. Para cada luminária válida, o programa calcula a distância até todas as referências válidas pela fórmula de Haversine. Essa fórmula considera a curvatura da Terra e devolve a distância geodésica em metros.

6. O cálculo é executado em blocos para reduzir o consumo de memória em bases grandes. Para cada luminária, é escolhida a referência com a menor distância.

7. O arquivo `resultado.csv` é gerado com as colunas:

   | Coluna | Descrição |
   | --- | --- |
   | `ID Nox` | Identificador único da luminária. |
   | `tipo_ponto` | Tipo da referência geográfica mais próxima. |
   | `nome` | Nome ou identificação da referência mais próxima. |
   | `Distância (m)` | Distância, em metros, entre a luminária e a referência. |

## Requisitos

- Python 3.10 ou posterior
- NumPy
- pandas

Instale as dependências com:

```bash
pip install numpy pandas
```

## Organização esperada dos dados

O arquivo de referências pode ficar versionado no repositório. Mantenha apenas os dados de luminárias em uma pasta local que não será versionada:

```text
pasta-de-dados/
├── referencias.csv
└── luminarias.csv
```

Defina a variável de ambiente apontando para essa pasta.

No PowerShell:

```powershell
$env:NOX_DADOS_DIR = "C:\caminho\privado\pasta-de-dados"
python associar_referencias.py
```

No Linux ou macOS:

```bash
NOX_DADOS_DIR="/caminho/privado/pasta-de-dados" python associar_referencias.py
```

O programa criará `resultado.csv` na mesma pasta indicada.

## Colunas aceitas

O programa aceita variações nos nomes de colunas mais comuns.

- Luminárias: `ID Nox` (ou `ID_Nox`), `latitude` (ou `lat`) e `longitude` (ou `lon`/`lng`).
- Referências: `Nome/identificação` (ou `nome do local`/`localização`), `tipo_ponto` (ou `Tipo de elemento`), `Latitude` (ou `lat`) e `Longitude` (ou `lon`/`lng`).

