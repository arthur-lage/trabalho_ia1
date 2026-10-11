# EC IA - Trabalho 01 - 2026/2

Material público do Trabalho 01 da disciplina de Inteligência Artificial.

## Informações principais

- **Valor:** 20,0 pontos.
- **Modalidade:** individual ou em dupla.
- **Linguagem:** Python.
- **Parte 1 - Busca não informada e informada:** entrega em **08/10/2026**.
- **Parte 2 - Busca local e entrega final:** entrega em **15/10/2026**.

Leia primeiro o arquivo **`EC_IA_Trabalho_01_2026.pdf`**. O enunciado prevalece sobre qualquer resumo apresentado neste README.

## Identificação da entrega

Preencha estes dados antes de cada submissão:

- **Aluno(a) 1:** `Arthur Batista Lage e Silva`
- **Aluno(a) 2:** `Rafael Ferreira da Rocha`
- **Repositório Git:** `https://github.com/arthur-lage/trabalho_ia1`
- **Tag:** `entrega-parte1`

## Entrega no SIGAA e repositório Git

O desenvolvimento deve ser mantido em um repositório Git acessível ao professor. O repositório deve permanecer **privado até o encerramento da correção**, com acesso concedido ao professor.

### 08/10/2026 - Parte 1

No SIGAA, envie um arquivo `.zip` com a versão executável da Parte 1. Antes da entrega, crie no repositório a tag:

```bash
git tag entrega-parte1
git push origin entrega-parte1
```

O `README.md` da entrega deve informar o endereço do repositório e a tag `entrega-parte1`. Não é necessário entregar o relatório final nesta etapa.

### 15/10/2026 - Entrega final

No SIGAA, envie:

- o relatório final em PDF;
- um arquivo `.zip` com o projeto completo.

Antes da entrega, crie no repositório a tag:

```bash
git tag entrega-final
git push origin entrega-final
```

O `README.md` e o relatório final devem informar o endereço do repositório e a tag `entrega-final`. A versão avaliada será a versão marcada por essa tag. Commits posteriores não substituem a versão entregue.

O histórico de commits poderá ser utilizado como elemento auxiliar na verificação da autoria e da contribuição dos integrantes, sem exigência de quantidade mínima de commits.

## Conteúdo deste pacote

```text
.
├── EC_IA_Trabalho_01_2026.pdf   # enunciado oficial
├── README.md                     # orientações gerais
├── IA_USAGE.md                   # registro do uso de IA
├── instrucoes_relatorio.md       # orientações para o relatório
├── .gitignore
├── requirements.txt
├── data/
│   └── mapa_teste.txt
├── src/
│   ├── __init__.py
│   ├── problem.py
│   ├── models.py
│   ├── heuristics.py
│   ├── search.py
│   ├── eight_queens.py
│   ├── hill_climbing.py
│   └── main.py
├── scripts/
│   └── run_experiments.py
├── tests/
│   ├── test_problem.py
│   ├── test_search.py
│   ├── test_eight_queens.py
│   └── test_hill_climbing.py
├── results/
│   ├── tabela_parte1.md
│   ├── tabela_parte1.csv
│   └── caminhos.txt
└── modelo_relatorio/
    ├── relatorio_sbc.tex
    └── sbc-template.sty
```

O fonte LaTeX do enunciado e os arquivos institucionais utilizados para sua composição não fazem parte do material de trabalho dos alunos.

## Parte 1 - Busca não informada e informada

Devem ser implementados:

- Busca em Largura - BFS;
- Busca em Profundidade - DFS;
- Busca de Custo Uniforme - UCS;
- Busca Gulosa;
- A*;
- heurísticas Manhattan e Euclidiana.

O mapa público está em `data/mapa_teste.txt`. O programa também será avaliado com mapas não disponibilizados previamente.

Exemplo de execução após a implementação:

```bash
python -m src.main busca --map data/mapa_teste.txt --algorithm astar --heuristic manhattan
```

## Parte 2 - Busca local

Devem ser implementados para o problema das 8 Rainhas:

- Hill Climbing;
- Random-Restart Hill Climbing.

Exemplos:

```bash
python -m src.main rainhas --algorithm hill --seed 42
python -m src.main rainhas --algorithm restart --seed 42 --max-restarts 50
```

As funções de 8 Rainhas ainda estão com `NotImplementedError` e não fazem parte desta entrega parcial.

## Testes da Parte 1

Execute todos os testes com:

```bash
python -m unittest discover -s tests -v
```

Os testes de Parte 1 cobrem casos de solução e falha, ciclos, desempate, custos ponderados, heurísticas, mapas não quadrados e comparação de A* com UCS em 200 mapas aleatórios reproduzíveis. Os testes de 8 Rainhas definem os casos de aceitação da Parte 2 e só passarão depois da implementação de `conflicts`, `moves`, Hill Climbing e Random-Restart.

## Experimentos

Gere a tabela e os mapas com os caminhos da Parte 1 a partir da raiz do repositório:

```bash
python -m scripts.run_experiments
```

O script executa cada configuração 30 vezes por padrão e calcula a mediana do tempo, sem incluir a leitura do mapa. Para usar outro mapa, informe `--map caminho/do/mapa.txt`; para aumentar as repetições, informe `--repeticoes N` (mínimo 30). Os resultados são gravados em `results/`.

Depois da implementação da Parte 2, rode os experimentos com as sementes de 0 a 99:

```bash
python -m scripts.run_experiments --parte 2
```

Esse modo resume taxa de sucesso, iterações e estados avaliados, além dos reinícios do Random-Restart. Também grava os resultados por semente em `results/experimentos_rainhas.csv`, a tabela agregada em `results/tabela_parte2.md` e os dados de uma falha do Hill Climbing em `results/falha_hill_climbing.md`. Use `--parte ambas` para executar as duas partes.

### Resultados preliminares no mapa público

A tabela abaixo foi gerada por `scripts/run_experiments.py` com `python -m scripts.run_experiments`.

<!-- TABELA_PARTE1_INICIO -->

| Alg. | Heur. | Passos | Custo | Ger. | Exp. | Pico F. | Pico Mem. | Tempo mediano (ms) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BFS | - | 15 | 40 | 66 | 59 | 9 | 66 | 0.083 |
| DFS | - | 15 | 40 | 21 | 15 | 6 | 21 | 0.025 |
| UCS | - | 29 | 29 | 77 | 74 | 6 | 77 | 0.187 |
| Gulosa | Manhattan | 15 | 40 | 21 | 15 | 6 | 21 | 0.029 |
| A* | Manhattan | 29 | 29 | 60 | 43 | 17 | 58 | 0.137 |
| Gulosa | Euclidiana | 15 | 40 | 21 | 15 | 6 | 21 | 0.030 |
| A* | Euclidiana | 29 | 29 | 72 | 60 | 12 | 72 | 0.184 |

<!-- TABELA_PARTE1_FIM -->

Os arquivos [`results/tabela_parte1.csv`](results/tabela_parte1.csv) e [`results/caminhos.txt`](results/caminhos.txt) contêm as saídas reproduzíveis do script. O mapa em texto identifica o percurso com `*` e preserva os marcadores `S` e `G`.

## Relatório

Consulte `instrucoes_relatorio.md` e a pasta `modelo_relatorio/`.

O relatório deve usar o modelo SBC fornecido, sem capa separada, respeitando o limite e os requisitos definidos no enunciado.

## Uso de Inteligência Artificial

Todo uso de ferramentas de IA deve obedecer à política descrita no enunciado e ser registrado em `IA_USAGE.md`.

## Estado da implementação

A Parte 1 contém as buscas BFS, DFS, UCS, Gulosa e A*, além das heurísticas Manhattan e Euclidiana. A Parte 2 permanece pendente para a próxima etapa do trabalho.
