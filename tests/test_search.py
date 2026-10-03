import unittest
from random import Random

from src.heuristics import euclidean, manhattan
from src.problem import WeightedGrid
from src.search import astar, bfs, dfs, greedy, uniform_cost


class SearchRequirementsTests(unittest.TestCase):

    def test_heuristics(self):
        self.assertEqual(manhattan((0, 0), (3, 4)), 7)
        self.assertEqual(euclidean((0, 0), (3, 4)), 5)
        self.assertEqual(manhattan((2, 3), (2, 3)), 0)
        self.assertEqual(euclidean((2, 3), (2, 3)), 0)

    def test_public_map_optimality_and_path_costs(self):
        grid = WeightedGrid.from_file("data/mapa_teste.txt")
        ucs_result = uniform_cost(grid)
        bfs_result = bfs(grid)
        dfs_result = dfs(grid)

        self.assertEqual(ucs_result.cost, 29)
        self.assertLessEqual(bfs_result.steps, ucs_result.steps)
        self.assertTrue(greedy(grid, manhattan).found)

        for result in (bfs_result, dfs_result):
            with self.subTest(algorithm=result.algorithm):
                self.assertEqual(
                    result.cost,
                    sum(grid.step_cost(pos) for pos in result.path[1:]),
                )

        for heuristic in (manhattan, euclidean):
            with self.subTest(heuristic=heuristic.__name__):
                result = astar(grid, heuristic)
                self.assertEqual(result.cost, ucs_result.cost)

    def test_astar_matches_ucs_on_seeded_random_maps(self):
        rng = Random(20261003)
        symbols = (".", ".", ".", "R", "M", "#")
        unsolved_maps = 0

        for map_index in range(200):
            height, width = rng.randint(3, 9), rng.randint(3, 9)
            start = (rng.randrange(height), rng.randrange(width))
            goal = start
            while goal == start:
                goal = (rng.randrange(height), rng.randrange(width))

            cells = [[rng.choice(symbols) for _ in range(width)] for _ in range(height)]
            cells[start[0]][start[1]] = "S"
            cells[goal[0]][goal[1]] = "G"
            grid = WeightedGrid(cells)
            expected = uniform_cost(grid)
            if not expected.found:
                unsolved_maps += 1

            for heuristic in (manhattan, euclidean):
                actual = astar(grid, heuristic)
                with self.subTest(map_index=map_index, heuristic=heuristic.__name__):
                    self.assertEqual(actual.found, expected.found)
                    if expected.found:
                        self.assertEqual(actual.cost, expected.cost)

        self.assertGreater(unsolved_maps, 0)
        self.assertLess(unsolved_maps, 200)

    def test_dfs_and_search_support_non_square_maps_and_arbitrary_endpoints(self):
        horizontal = WeightedGrid([list("...SG")])
        vertical = WeightedGrid([list("."), list("."), list("G"), list("."), list("S")])

        for grid in (horizontal, vertical):
            for search in (bfs, dfs, uniform_cost):
                result = search(grid)
                with self.subTest(shape=(grid.height, grid.width), algorithm=result.algorithm):
                    self.assertTrue(result.found)
                    self.assertEqual(result.path[0], grid.start)
                    self.assertEqual(result.path[-1], grid.goal)

    def test_dfs_successor_expansion_respects_required_order(self):
        grid = WeightedGrid(
            [
                list("....."),
                list("....."),
                list("..S.."),
                list("....."),
                list("....G"),
            ]
        )
        result = dfs(grid)
        self.assertTrue(result.found)
        self.assertEqual(result.path[1], (1, 2))  # Norte é inserido por último e retirado primeiro.

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
            greedy(grid, euclidean),
            astar(grid, manhattan),
            astar(grid, euclidean),
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
