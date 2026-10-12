from random import Random
from typing import Iterable, List, Tuple

Board = List[int]
Move = Tuple[int, int]  # (coluna, nova_linha)
N = 8


def initial_board(rng: Random) -> Board:
    """Geração padronizada: uma rainha aleatória por coluna."""
    return [rng.randrange(N) for _ in range(N)]


def conflicts(board: Board) -> int:
    """Retorne o número de pares não ordenados de rainhas que se atacam."""
    count = 0
    for i in range(N):
        for j in range(i + 1, N):
            if board[i] == board[j]:  # mesma linha
                count += 1
            elif abs(board[i] - board[j]) == abs(i - j):  # mesma diagonal
                count += 1
    return count


def moves(board: Board) -> Iterable[Move]:
    """
    Gere a vizinhança na ordem obrigatória:
    coluna 0..7; dentro de cada coluna, linha 0..7, exceto a linha atual.
    """
    for col in range(N):
        for row in range(N):
            if row != board[col]:
                yield (col, row)


def apply_move(board: Board, move: Move) -> Board:
    col, row = move
    if not 0 <= col < N or not 0 <= row < N:
        raise ValueError("Movimento fora do tabuleiro.")
    new_board = board.copy()
    new_board[col] = row
    return new_board


def render(board: Board) -> str:
    rows = []
    for r in range(N):
        rows.append(" ".join("Q" if board[c] == r else "." for c in range(N)))
    return "\n".join(rows)
