# Análise de dados de iluminação pública – Projeto Smart Cities

Este repositório reúne códigos desenvolvidos para o processamento, a análise e a visualização de dados de sistemas de iluminação pública, utilizando informações provenientes da plataforma de telegestão Nox.

O projeto tem como objetivo explorar técnicas de análise de dados para monitorar o funcionamento das luminárias, identificar inconsistências e possíveis anomalias nos registros operacionais, avaliar padrões de consumo energético e investigar a distribuição espacial dos equipamentos.

Atualmente, o repositório contempla três frentes principais:

- **Análise espacial:** associação de IDs Nox a referências geográficas próximas.
- **Análise de anomalias:** identificação e avaliação de divergências nos indicadores de consumo e funcionamento.
- **Visualização de dados:** geração de gráficos para exploração dos dados e interpretação dos resultados.

## Privacidade e dados ocultados

Este repositório foi preparado para ser compartilhado sem revelar informações pessoais, institucionais ou operacionais que não são necessárias para compreender ou executar os algoritmos.

Foram ocultados ou generalizados:

- O caminho local completo dos dados, que continha nome de usuário, serviço de armazenamento, curso e contexto do projeto.
- Os nomes originais dos arquivos de entrada e saída, substituídos por nomes neutros, como `referencias.csv`, `luminarias.csv` e `resultado.csv`.
- A localização física dos arquivos no computador. Ela é informada em tempo de execução pela variável de ambiente `NOX_DADOS_DIR`.
- Mensagens de erro que poderiam revelar a estrutura interna das tabelas, como a lista completa de colunas disponíveis.

O arquivo `referencias.csv` pode ser incluído no repositório, pois suas referências estão autorizadas para disponibilização. Já os arquivos contendo dados operacionais das luminárias não devem ser publicados sem uma revisão específica, pois podem conter identificadores, coordenadas ou leituras que exijam proteção.

## 1. Análise espacial

Esta etapa relaciona cada **ID Nox** à referência geográfica mais próxima, como um ponto de infraestrutura, estacionamento ou outro elemento cadastrado.

O resultado é exportado em formato CSV, contendo o identificador da luminária, o tipo e o nome da referência encontrada e a distância calculada em metros.

### Como o código funciona

1. O programa lê dois arquivos CSV:
   - `referencias.csv`: contém os pontos de referência, seus tipos, nomes e coordenadas.
   - `luminarias.csv`: contém os IDs Nox e as coordenadas das luminárias.

2. Os cabeçalhos são normalizados para tolerar diferenças de maiúsculas, acentos e espaços.

3. As coordenadas são convertidas para números, aceitando valores com vírgula ou ponto decimal. Linhas com coordenadas inválidas — incluindo a coordenada nula `(0, 0)` para luminárias — não recebem uma referência próxima.

4. Caso existam várias leituras para o mesmo ID Nox, apenas a primeira é mantida, pois as coordenadas são consideradas iguais para aquele identificador.

5. Para cada luminária válida, o programa calcula a distância até todas as referências válidas pela fórmula de Haversine, que considera a curvatura da Terra e retorna a distância geodésica em metros.

6. O cálculo é executado em blocos para reduzir o consumo de memória em bases grandes. Para cada luminária, é escolhida a referência com a menor distância.

7. O arquivo `resultado.csv` é gerado com as seguintes colunas:

| Coluna | Descrição |
| --- | --- |
| `ID Nox` | Identificador único da luminária. |
| `tipo_ponto` | Tipo da referência geográfica mais próxima. |
| `nome` | Nome ou identificação da referência mais próxima. |
| `Distância (m)` | Distância, em metros, entre a luminária e a referência. |

## 2. Análise de anomalias

Esta etapa reúne códigos destinados à identificação e à avaliação de comportamentos atípicos nos registros de consumo e funcionamento das luminárias.

A análise utiliza indicadores derivados dos dados operacionais, permitindo investigar divergências entre o comportamento esperado e o observado.

Entre as variáveis consideradas estão:

- Potência cadastrada;
- Consumo real;
- Consumo estimado;
- Consumo por tempo;
- Tempo ligado;
- Tempo de escuridão;
- Duração do intervalo de medição;
- Desvios absolutos e relativos entre indicadores.

### Objetivos da análise

- Identificar registros com divergências entre consumo real e estimado.
- Investigar luminárias cujo tempo ligado ultrapassa a duração do intervalo de medição.
- Identificar valores atípicos nos indicadores de consumo e funcionamento.
- Avaliar a distribuição das divergências entre diferentes grupos de luminárias.
- Diferenciar possíveis falhas operacionais de inconsistências nos registros ou na medição.

A identificação de um registro anômalo não significa necessariamente que exista uma falha física na luminária. Os resultados devem ser interpretados considerando as características dos dados, os intervalos de leitura e as limitações dos dispositivos de monitoramento.

## 3. Visualização de dados

O repositório também contém códigos para geração de gráficos utilizados na análise exploratória e na interpretação dos resultados.

As visualizações permitem observar distribuições, comparar indicadores e identificar padrões que podem não ser evidentes apenas pela análise das tabelas.

Entre as possibilidades de visualização contempladas estão:

- Distribuições de consumo energético;
- Comparações entre consumo real e estimado;
- Distribuição dos desvios absolutos e relativos;
- Comparações entre categorias de luminárias e tipos de referência;
- Relações entre tempo ligado e consumo;
- Distribuição de registros classificados como divergentes;
- Comparações entre grupos e categorias de análise.

Os gráficos auxiliam na interpretação dos indicadores e na identificação de padrões espaciais e operacionais, contribuindo para uma avaliação mais abrangente do funcionamento do sistema de iluminação pública.

## Colunas aceitas na análise espacial

O programa de associação espacial aceita variações nos nomes de colunas mais comuns.

- **Luminárias:** `ID Nox` (ou `ID_Nox`), `latitude` (ou `lat`) e `longitude` (ou `lon`/`lng`).
- **Referências:** `Nome/identificação` (ou `nome do local`/`localização`), `tipo_ponto` (ou `Tipo de elemento`), `Latitude` (ou `lat`) e `Longitude` (ou `lon`/`lng`).

## Observações

Os códigos deste repositório foram desenvolvidos no contexto do Projeto Final de Curso sobre Aplicação de Ciência de Dados no Monitoramento de Sistemas de Iluminação Pública em Cidades Inteligentes de Tamyris Cabral

As implementações podem ser utilizadas como referência para estudos relacionados à eficiência energética, monitoramento remoto, identificação de anomalias e análise espacial de infraestrutura urbana.
