from dataclasses import dataclass, field
from random import Random
from typing import List

from .eight_queens import Board, initial_board, conflicts, moves, apply_move


@dataclass
class HillResult:
    success: bool
    initial: Board
    final: Board
    initial_conflicts: int
    final_conflicts: int
    iterations: int
    evaluated_states: int
    restarts: int = 0
    history: List[int] = field(default_factory=list)


def hill_climbing(initial: Board) -> HillResult:
    """
    Hill Climbing básico, sem movimentos laterais.
    Deve escolher o primeiro melhor vizinho conforme a ordem de vizinhança definida.
    """


    current = initial.copy()
    current_h = conflicts(current)
    evaluated_states = 1
    iterations = 0
    initial_conflicts = current_h
    initial_board_snapshot = initial.copy()

    while True:
        best_neighbor = None
        best_h = current_h

        for move in moves(current):
            neighbor = apply_move(current, move)
            h = conflicts(neighbor)
            evaluated_states += 1
            if h < best_h:
                best_h = h
                best_neighbor = neighbor
                break  # primeiro melhor vizinho na ordem obrigatória

        if best_neighbor is None:
            break

        current = best_neighbor
        current_h = best_h
        iterations += 1

    return HillResult(
        success=(current_h == 0),
        initial=initial_board_snapshot,
        final=current,
        initial_conflicts=initial_conflicts,
        final_conflicts=current_h,
        iterations=iterations,
        evaluated_states=evaluated_states,
    )


def random_restart(rng: Random, max_restarts: int = 50) -> HillResult:
    """
    Execute Hill Climbing com reinícios aleatórios até encontrar solução
    ou atingir max_restarts.
    """


    board = initial_board(rng)
    result = hill_climbing(board)

    first_initial = result.initial
    first_initial_conflicts = result.initial_conflicts
    total_iterations = result.iterations
    total_evaluated = result.evaluated_states
    restarts = 0

    if result.success:
        return HillResult(
            success=True,
            initial=first_initial,
            final=result.final,
            initial_conflicts=first_initial_conflicts,
            final_conflicts=result.final_conflicts,
            iterations=total_iterations,
            evaluated_states=total_evaluated,
            restarts=0,
        )

    for _ in range(max_restarts):
        restarts += 1
        board = initial_board(rng)
        result = hill_climbing(board)
        total_iterations += result.iterations
        total_evaluated += result.evaluated_states

        if result.success:
            break

    return HillResult(
        success=result.success,
        initial=first_initial,
        final=result.final,
        initial_conflicts=first_initial_conflicts,
        final_conflicts=result.final_conflicts,
        iterations=total_iterations,
        evaluated_states=total_evaluated,
        restarts=restarts,
    )

