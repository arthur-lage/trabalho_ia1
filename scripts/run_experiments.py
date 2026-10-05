"""Executa e registra os experimentos da Parte 1 em uma grade ponderada."""

import argparse
import csv
import statistics
import time
from pathlib import Path
from typing import Callable

from src.heuristics import euclidean, manhattan
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


def _positive_repetitions(value: str) -> int:
    repetitions = int(value)
    if repetitions < 30:
        raise argparse.ArgumentTypeError("Use pelo menos 30 repetições.")
    return repetitions


def main() -> None:
    parser = argparse.ArgumentParser(description="Experimentos reproduzíveis da Parte 1.")
    parser.add_argument("--map", type=Path, default=MAPA_PADRAO, help="Arquivo de mapa.")
    parser.add_argument("--repeticoes", type=_positive_repetitions, default=REPETICOES)
    args = parser.parse_args()

    # O mapa é lido uma vez; somente as chamadas dos algoritmos são cronometradas.
    problem = WeightedGrid.from_file(args.map)
    RESULTS.mkdir(parents=True, exist_ok=True)
    rows = _experiment(problem, args.repeticoes)
    _write_tables(rows)
    _write_path_text(problem, rows)
    print(f"\nArquivos gerados em: {RESULTS}")
    print("Parte 2: TODO - experimentos de oito rainhas ficam para a proxima etapa.")


if __name__ == "__main__":
    main()
