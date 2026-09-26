import unittest

from src.heuristics import euclidean, manhattan
from src.problem import WeightedGrid
from src.search import astar, bfs, dfs, greedy, uniform_cost


class SearchRequirementsTests(unittest.TestCase):

    def test_start_adjacent_to_goal(self):
        # tests when start is next to goal
        grid = WeightedGrid(
            [
                list("SG"),
                list("##"),
            ]
        )

        res_bfs = bfs(grid)
        self.assertTrue(res_bfs.found)
        self.assertEqual(res_bfs.steps, 1)
        self.assertEqual(res_bfs.actions, ["L"])
        self.assertEqual(res_bfs.path, [(0, 0), (0, 1)])
        self.assertEqual(res_bfs.cost, 1)

        res_ucs = uniform_cost(grid)
        self.assertTrue(res_ucs.found)
        self.assertEqual(res_ucs.steps, 1)
        self.assertEqual(res_ucs.cost, 1)

    def test_unsolvable_map(self):
        # tests map with no possible path
        grid = WeightedGrid(
            [
                list("S#G"),
                list(".#."),
            ]
        )

        algorithms = [
            bfs(grid),
            dfs(grid),
            uniform_cost(grid),
            greedy(grid, manhattan),
            astar(grid, manhattan),
        ]

        for res in algorithms:
            with self.subTest(algorithm=res.algorithm):
                self.assertFalse(res.found)
                self.assertEqual(res.path, [])
                self.assertEqual(res.actions, [])
                self.assertEqual(res.cost, float("inf"))

    def test_map_with_cycles(self):
        # tests map with cycle to check for loops
        grid = WeightedGrid(
            [
                list("S.."),
                list(".#."),
                list("..G"),
            ]
        )

        for res in [
            bfs(grid),
            dfs(grid),
            uniform_cost(grid),
            greedy(grid, manhattan),
            astar(grid, manhattan),
        ]:
            with self.subTest(algorithm=res.algorithm):
                self.assertTrue(res.found)
                self.assertGreater(len(res.path), 0)
                self.assertEqual(res.path[0], grid.start)
                self.assertEqual(res.path[-1], grid.goal)

    def test_distinct_routes_same_step_count(self):
        # checks tie breaking order n, l, s, o
        grid = WeightedGrid(
            [
                list("S.."),
                list(".#."),
                list("..G"),
            ]
        )

        # top path is l, l, s, s and bottom is s, s, l, l
        res_bfs = bfs(grid)
        self.assertTrue(res_bfs.found)
        self.assertEqual(res_bfs.steps, 4)
        self.assertEqual(res_bfs.actions, ["L", "L", "S", "S"])

    def test_short_expensive_vs_long_cheap_route(self):
        # compares shortest path vs cheapest path
        grid = WeightedGrid(
            [
                list("SMMG"),
                list("...."),
            ]
        )

        # bfs chooses shorter path with 3 steps
        res_bfs = bfs(grid)
        self.assertTrue(res_bfs.found)
        self.assertEqual(res_bfs.steps, 3)
        self.assertEqual(res_bfs.cost, 13)
        self.assertEqual(res_bfs.actions, ["L", "L", "L"])

        # ucs chooses cheaper path with 5 steps
        res_ucs = uniform_cost(grid)
        self.assertTrue(res_ucs.found)
        self.assertEqual(res_ucs.steps, 5)
        self.assertEqual(res_ucs.cost, 5)
        self.assertEqual(res_ucs.actions, ["S", "L", "L", "L", "N"])

        # astar also finds the cheaper path
        res_astar = astar(grid, manhattan)
        self.assertTrue(res_astar.found)
        self.assertEqual(res_astar.steps, 5)
        self.assertEqual(res_astar.cost, 5)
        self.assertEqual(res_astar.actions, ["S", "L", "L", "L", "N"])


if __name__ == "__main__":
    unittest.main()
