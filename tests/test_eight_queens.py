import unittest
from random import Random

from src.eight_queens import (
    N,
    apply_move,
    conflicts,
    initial_board,
    moves,
    render,
)


SOLUTION = [0, 4, 7, 5, 2, 6, 1, 3]


class EightQueensModelTests(unittest.TestCase):
    def test_known_solution_has_no_conflicts(self):
        self.assertEqual(conflicts(SOLUTION), 0)

    def test_conflicts_count_unordered_pairs(self):
        self.assertEqual(conflicts([0] * N), 28)  # Todos os pares compartilham linha.
        self.assertEqual(conflicts(list(range(N))), 28)  # Todos os pares estão na diagonal.

    def test_moves_has_56_entries_in_required_order(self):
        expected = [
            (column, row)
            for column in range(N)
            for row in range(N)
            if row != SOLUTION[column]
        ]
        self.assertEqual(list(moves(SOLUTION)), expected)
        self.assertEqual(len(expected), 56)

    def test_moves_does_not_modify_board(self):
        board = SOLUTION.copy()
        list(moves(board))
        self.assertEqual(board, SOLUTION)

    def test_initial_board_uses_eight_seeded_randrange_calls(self):
        seed = 1729
        expected_rng = Random(seed)
        expected = [expected_rng.randrange(8) for _ in range(8)]
        self.assertEqual(initial_board(Random(seed)), expected)

    def test_apply_move_returns_a_new_board(self):
        board = SOLUTION.copy()
        changed = apply_move(board, (2, 0))
        self.assertEqual(changed[2], 0)
        self.assertEqual(board, SOLUTION)
        self.assertIsNot(changed, board)

    def test_apply_move_rejects_invalid_coordinates(self):
        for move in ((-1, 0), (N, 0), (0, -1), (0, N)):
            with self.subTest(move=move):
                with self.assertRaises(ValueError):
                    apply_move(SOLUTION, move)

    def test_render_places_one_queen_per_column(self):
        rendered = render(SOLUTION).splitlines()
        self.assertEqual(len(rendered), N)
        self.assertTrue(all(len(row.split()) == N for row in rendered))
        self.assertEqual(sum(row.split().count("Q") for row in rendered), N)


if __name__ == "__main__":
    unittest.main()
