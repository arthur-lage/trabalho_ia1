import unittest
from random import Random
from unittest.mock import Mock, patch

from src.eight_queens import apply_move, conflicts, initial_board, moves
from src import hill_climbing as hill_module
from src.hill_climbing import HillResult, hill_climbing, random_restart


SOLUTION = [0, 4, 7, 5, 2, 6, 1, 3]


class HillClimbingTests(unittest.TestCase):
    def test_solved_initial_board_returns_success_without_moves(self):
        result = hill_climbing(SOLUTION.copy())

        self.assertTrue(result.success)
        self.assertEqual(result.initial, SOLUTION)
        self.assertEqual(result.final, SOLUTION)
        self.assertEqual(result.initial_conflicts, 0)
        self.assertEqual(result.final_conflicts, 0)
        self.assertEqual(result.iterations, 0)
        self.assertGreaterEqual(result.evaluated_states, 1)

    def test_result_conflict_fields_match_initial_and_final_boards(self):
        initial = [0] * 8
        result = hill_climbing(initial)

        self.assertEqual(result.initial, initial)
        self.assertEqual(result.initial_conflicts, conflicts(initial))
        self.assertEqual(result.final_conflicts, conflicts(result.final))
        self.assertEqual(result.success, result.final_conflicts == 0)
        self.assertGreaterEqual(result.iterations, 0)
        self.assertGreaterEqual(result.evaluated_states, 1)

    def test_hill_climbing_does_not_change_the_input_board(self):
        initial = [0] * 8
        snapshot = initial.copy()
        hill_climbing(initial)
        self.assertEqual(initial, snapshot)

    def test_plateau_does_not_count_as_an_improving_move(self):
        initial = SOLUTION.copy()
        measured = Mock(return_value=5)
        with (
            patch("src.eight_queens.conflicts", measured),
            patch.object(hill_module, "conflicts", measured, create=True),
        ):
            result = hill_climbing(initial)

        self.assertEqual(result.final, initial)
        self.assertEqual(result.iterations, 0)
        self.assertEqual(result.evaluated_states, measured.call_count)

    def test_equal_best_neighbors_choose_first_in_required_order(self):
        initial = SOLUTION.copy()
        legal_moves = list(moves(initial))
        first_move = legal_moves[0]
        tied_move = next(move for move in legal_moves if move[0] != first_move[0])
        first_board = apply_move(initial, first_move)
        tied_board = apply_move(initial, tied_move)

        def objective(board):
            if board == initial:
                return 10
            if board == first_board or board == tied_board:
                return 4
            return 6

        measured = Mock(side_effect=objective)
        with (
            patch("src.eight_queens.conflicts", measured),
            patch.object(hill_module, "conflicts", measured, create=True),
        ):
            result = hill_climbing(initial)

        self.assertEqual(result.final, first_board)
        self.assertEqual(result.iterations, 1)
        self.assertEqual(result.evaluated_states, measured.call_count)


class RandomRestartTests(unittest.TestCase):
    def test_zero_restarts_runs_the_seeded_initial_attempt(self):
        seed = 42
        expected_initial = initial_board(Random(seed))
        expected = hill_climbing(expected_initial)
        actual = random_restart(Random(seed), max_restarts=0)

        self.assertEqual(actual.initial, expected.initial)
        self.assertEqual(actual.final, expected.final)
        self.assertEqual(actual.initial_conflicts, expected.initial_conflicts)
        self.assertEqual(actual.final_conflicts, expected.final_conflicts)
        self.assertEqual(actual.iterations, expected.iterations)
        self.assertEqual(actual.evaluated_states, expected.evaluated_states)
        self.assertEqual(actual.restarts, 0)
        self.assertEqual(actual.success, expected.success)

    def test_same_seed_produces_same_random_restart_result(self):
        first = random_restart(Random(2026), max_restarts=50)
        second = random_restart(Random(2026), max_restarts=50)

        for field in (
            "success",
            "initial",
            "final",
            "initial_conflicts",
            "final_conflicts",
            "iterations",
            "evaluated_states",
            "restarts",
        ):
            with self.subTest(field=field):
                self.assertEqual(getattr(first, field), getattr(second, field))

    def test_random_restart_respects_the_restart_limit(self):
        limit = 3
        result = random_restart(Random(11), max_restarts=limit)
        self.assertGreaterEqual(result.restarts, 0)
        self.assertLessEqual(result.restarts, limit)

    def test_random_restart_aggregates_metrics_and_reuses_rng(self):
        failed = HillResult(False, [0] * 8, [1] * 8, 28, 10, 2, 57)
        succeeded = HillResult(True, [2] * 8, SOLUTION.copy(), 8, 0, 3, 91)
        results = iter((failed, succeeded))
        generated_boards = iter(([0] * 8, [2] * 8))
        rng_objects = []

        def make_initial(rng):
            rng_objects.append(rng)
            return next(generated_boards)

        with (
            patch.object(hill_module, "initial_board", side_effect=make_initial, create=True),
            patch.object(hill_module, "hill_climbing", side_effect=lambda _: next(results)),
        ):
            combined = hill_module.random_restart(Random(5), max_restarts=5)

        self.assertEqual(len(rng_objects), 2)
        self.assertIs(rng_objects[0], rng_objects[1])
        self.assertTrue(combined.success)
        self.assertEqual(combined.initial, failed.initial)
        self.assertEqual(combined.final, succeeded.final)
        self.assertEqual(combined.initial_conflicts, failed.initial_conflicts)
        self.assertEqual(combined.final_conflicts, succeeded.final_conflicts)
        self.assertEqual(combined.iterations, failed.iterations + succeeded.iterations)
        self.assertEqual(
            combined.evaluated_states,
            failed.evaluated_states + succeeded.evaluated_states,
        )
        self.assertEqual(combined.restarts, 1)

    def test_fifty_restarts_allow_at_most_fifty_one_attempts(self):
        failed = HillResult(False, [0] * 8, [0] * 8, 28, 28, 0, 57)
        attempts = []

        def make_initial(_rng):
            board = [len(attempts) % 8] * 8
            attempts.append(board)
            return board

        with (
            patch.object(hill_module, "initial_board", side_effect=make_initial, create=True),
            patch.object(hill_module, "hill_climbing", return_value=failed),
        ):
            combined = hill_module.random_restart(Random(6), max_restarts=50)

        self.assertEqual(len(attempts), 51)
        self.assertEqual(combined.restarts, 50)
        self.assertEqual(combined.iterations, 0)
        self.assertEqual(combined.evaluated_states, 51 * failed.evaluated_states)

    def test_restart_result_is_a_hill_result(self):
        result = random_restart(Random(12), max_restarts=0)
        self.assertIsInstance(result, HillResult)


if __name__ == "__main__":
    unittest.main()
