"""Executa e registra os experimentos das Partes 1 e 2 do trabalho."""

import argparse
import csv
import json
import statistics
import time
from pathlib import Path
from random import Random
from typing import Callable

from src.eight_queens import initial_board, render
from src.heuristics import euclidean, manhattan
from src.hill_climbing import hill_climbing, random_restart
from src.models import SearchResult
from src.problem import WeightedGrid
from src.search import astar, bfs, dfs, greedy, uniform_cost

ROOT = Path(__file__).resolve().parent.parent
MAPA_PADRAO = ROOT / "data" / "mapa_teste.txt"
RESULTS = ROOT / "results"
REPETICOES = 30

Search = Callable[[WeightedGrid], SearchResult]
CONFIGURACOES: tuple[tuple[str, str, Search], ...] = (
    ("BFS", "-", bfs),
    ("DFS", "-", dfs),
    ("UCS", "-", uniform_cost),
    ("Gulosa", "Manhattan", lambda problem: greedy(problem, manhattan)),
    ("A*", "Manhattan", lambda problem: astar(problem, manhattan)),
    ("Gulosa", "Euclidiana", lambda problem: greedy(problem, euclidean)),
    ("A*", "Euclidiana", lambda problem: astar(problem, euclidean)),
)
CABECALHOS = (
    "Alg.",
    "Heur.",
    "Passos",
    "Custo",
    "Ger.",
    "Exp.",
    "Pico F.",
    "Pico Mem.",
    "Tempo mediano (ms)",
)


def _format_cost(cost: float) -> str:
    if cost == float("inf"):
        return "∞"
    return str(int(cost)) if int(cost) == cost else f"{cost:.3f}"


def _experiment(problem: WeightedGrid, repetitions: int) -> list[dict[str, str | int]]:
    rows = []
    for algorithm, heuristic_name, search in CONFIGURACOES:
        samples_ms = []
        result = None
        for _ in range(repetitions):
            start = time.perf_counter()
            current = search(problem)
            samples_ms.append((time.perf_counter() - start) * 1000)
            if result is None:
                result = current
            else:
                metrics = (
                    "found",
                    "steps",
                    "cost",
                    "generated",
                    "expanded",
                    "peak_frontier",
                    "peak_stored_states",
                )
                if any(getattr(current, metric) != getattr(result, metric) for metric in metrics):
                    raise RuntimeError(
                        f"Métricas de {algorithm}/{heuristic_name} variaram entre execuções."
                    )

        assert result is not None
        rows.append(
            {
                "Alg.": algorithm,
                "Heur.": heuristic_name,
                "Passos": result.steps if result.found else "—",
                "Custo": _format_cost(result.cost),
                "Ger.": result.generated,
                "Exp.": result.expanded,
                "Pico F.": result.peak_frontier,
                "Pico Mem.": result.peak_stored_states,
                "Tempo mediano (ms)": f"{statistics.median(samples_ms):.3f}",
                "result": result,
            }
        )
    return rows


def _write_tables(rows: list[dict[str, str | int]]) -> None:
    headers = CABECALHOS
    markdown = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        markdown.append("| " + " | ".join(str(row[header]) for header in headers) + " |")

    (RESULTS / "tabela_parte1.md").write_text("\n".join(markdown) + "\n", encoding="utf-8")
    with (RESULTS / "tabela_parte1.csv").open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=headers, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print("\n".join(markdown))


def _write_path_text(problem: WeightedGrid, rows: list[dict[str, str | int]]) -> None:
    blocks = []
    for row in rows:
        result = row["result"]
        assert isinstance(result, SearchResult)
        title = (
            f"{row['Alg.']} | heurística: {row['Heur.']} | "
            f"passos: {row['Passos']} | custo: {row['Custo']}"
        )
        rendered = problem.render_path(result.path) if result.found else "Sem solução."
        blocks.append(f"{title}\n{rendered}")
    (RESULTS / "caminhos.txt").write_text("\n\n".join(blocks) + "\n", encoding="utf-8")


def _run_queens_experiments() -> None:
    """Agrega os experimentos da Parte 2 sem alterar os algoritmos de busca local."""
    raw_rows: list[dict[str, object]] = []
    hill_failure = None

    for seed in range(100):
        hill_rng = Random(seed)
        hill_initial = initial_board(hill_rng)
        hill_result = hill_climbing(hill_initial)

        restart_result = random_restart(Random(seed), max_restarts=50)
        for name, result in (
            ("Hill Climbing", hill_result),
            ("Random-Restart Hill Climbing", restart_result),
        ):
            raw_rows.append(
                {
                    "Algoritmo": name,
                    "Semente": seed,
                    "Sucesso": result.success,
                    "Iteracoes": result.iterations,
                    "Estados avaliados": result.evaluated_states,
                    "Reinicios": result.restarts,
                    "Conflitos iniciais": result.initial_conflicts,
                    "Conflitos finais": result.final_conflicts,
                    "Estado inicial": json.dumps(result.initial),
                    "Estado final": json.dumps(result.final),
                }
            )

        if not hill_result.success and hill_failure is None:
            hill_failure = hill_result
            hill_failure_seed = seed

    raw_fields = list(raw_rows[0])
    with (RESULTS / "experimentos_rainhas.csv").open(
        "w", encoding="utf-8-sig", newline=""
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=raw_fields)
        writer.writeheader()
        writer.writerows(raw_rows)

    summary = [
        "| Método | Sucesso | Média iterações | Mediana iterações | Média estados avaliados | Média reinícios | Máximo reinícios |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for name in ("Hill Climbing", "Random-Restart Hill Climbing"):
        method_rows = [row for row in raw_rows if row["Algoritmo"] == name]
        successes = sum(bool(row["Sucesso"]) for row in method_rows)
        iterations = [int(row["Iteracoes"]) for row in method_rows]
        evaluations = [int(row["Estados avaliados"]) for row in method_rows]
        restart_counts = [int(row["Reinicios"]) for row in method_rows]
        restarts_mean = f"{statistics.mean(restart_counts):.2f}" if name.startswith("Random") else "—"
        restarts_max = str(max(restart_counts)) if name.startswith("Random") else "—"
        summary.append(
            f"| {name} | {successes}% | {statistics.mean(iterations):.2f} | "
            f"{statistics.median(iterations):.2f} | {statistics.mean(evaluations):.2f} | "
            f"{restarts_mean} | {restarts_max} |"
        )
    (RESULTS / "tabela_parte2.md").write_text("\n".join(summary) + "\n", encoding="utf-8")
    print("\n".join(summary))

    if hill_failure is None:
        failure_text = (
            "Nenhuma falha do Hill Climbing ocorreu nas sementes 0..99; "
            "é necessário selecionar outro conjunto de execuções para cumprir "
            "a análise de falha solicitada no relatório.\n"
        )
    else:
        failure_text = (
            f"Falha do Hill Climbing na semente {hill_failure_seed}.\n\n"
            f"Estado inicial: {json.dumps(hill_failure.initial)}\n"
            f"Conflitos iniciais: {hill_failure.initial_conflicts}\n\n"
            f"Estado final: {json.dumps(hill_failure.final)}\n"
            f"Conflitos finais: {hill_failure.final_conflicts}\n\n"
            f"Tabuleiro inicial:\n{render(hill_failure.initial)}\n\n"
            f"Tabuleiro final:\n{render(hill_failure.final)}\n"
        )
    (RESULTS / "falha_hill_climbing.md").write_text(failure_text, encoding="utf-8")


def _positive_repetitions(value: str) -> int:
    repetitions = int(value)
    if repetitions < 30:
        raise argparse.ArgumentTypeError("Use pelo menos 30 repetições.")
    return repetitions


def main() -> None:
    parser = argparse.ArgumentParser(description="Experimentos reproduzíveis do Trabalho 01.")
    parser.add_argument("--parte", choices=("1", "2", "ambas"), default="1")
    parser.add_argument("--map", type=Path, default=MAPA_PADRAO, help="Arquivo de mapa.")
    parser.add_argument("--repeticoes", type=_positive_repetitions, default=REPETICOES)
    args = parser.parse_args()

    RESULTS.mkdir(parents=True, exist_ok=True)
    if args.parte in {"1", "ambas"}:
        # O mapa é lido uma vez; só as buscas são cronometradas.
        problem = WeightedGrid.from_file(args.map)
        rows = _experiment(problem, args.repeticoes)
        _write_tables(rows)
        _write_path_text(problem, rows)
    if args.parte in {"2", "ambas"}:
        _run_queens_experiments()
    print(f"\nArquivos gerados em: {RESULTS}")


if __name__ == "__main__":
    main()
