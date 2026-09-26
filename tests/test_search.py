import unittest

from src.heuristics import euclidean, manhattan
from src.problem import WeightedGrid
from src.search import astar, bfs, dfs, greedy, uniform_cost


class SearchRequirementsTests(unittest.TestCase):
    """
    Testes mínimos obrigatórios especificados na Seção 2.8 do enunciado:
    1. Início adjacente ao objetivo;
    2. Mapa sem solução;
    3. Mapa com ciclos;
    4. Existência de rotas distintas com o mesmo número de ações;
    5. Existência de uma rota curta e cara e outra mais longa e barata.
    """

    def test_start_adjacent_to_goal(self):
        """1. Caso de teste: Início adjacente ao objetivo (distância de 1 passo)."""
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
        """2. Caso de teste: Mapa sem solução (objetivo isolado por obstáculos)."""
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
        """3. Caso de teste: Mapa com ciclos (anel com repetição potencial de estados)."""
        # Formato de anel 3x3 com obstáculo no centro
        grid = WeightedGrid(
            [
                list("S.."),
                list(".#."),
                list("..G"),
            ]
        )

        # Garante que nenhum algoritmo entra em loop infinito e todos encontram o caminho
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
        """
        4. Caso de teste: Existência de rotas distintas com o mesmo número de ações.
        Verifica se a ordem obrigatória de desempate (N -> L -> S -> O) é respeitada.
        """
        grid = WeightedGrid(
            [
                list("S.."),
                list(".#."),
                list("..G"),
            ]
        )

        # Rota 1 (por cima): L, L, S, S (4 passos)
        # Rota 2 (por baixo): S, S, L, L (4 passos)
        # Ambas possuem 4 ações e custo 4.
        # Pela ordem lógica N -> L -> S -> O, o sucessor L é explorado antes de S.
        res_bfs = bfs(grid)
        self.assertTrue(res_bfs.found)
        self.assertEqual(res_bfs.steps, 4)
        self.assertEqual(res_bfs.actions, ["L", "L", "S", "S"])

    def test_short_expensive_vs_long_cheap_route(self):
        """
        5. Caso de teste: Existência de rota curta e cara vs rota mais longa e barata.
        Demonstra a diferença fundamental de optimalidade entre BFS e UCS/A*.
        """
        grid = WeightedGrid(
            [
                list("SMMG"),  # Rota curta: 3 passos, custo: 6 + 6 + 1 = 13
                list("...."),  # Rota longa: 5 passos (S, L, L, L, N), custo: 1 + 1 + 1 + 1 + 1 = 5
            ]
        )

        # BFS minimiza número de ações (profundidade): escolhe a rota de 3 passos, mais cara
        res_bfs = bfs(grid)
        self.assertTrue(res_bfs.found)
        self.assertEqual(res_bfs.steps, 3)
        self.assertEqual(res_bfs.cost, 13)
        self.assertEqual(res_bfs.actions, ["L", "L", "L"])

        # UCS minimiza o custo do caminho: prefere a rota de 5 passos, mais barata
        res_ucs = uniform_cost(grid)
        self.assertTrue(res_ucs.found)
        self.assertEqual(res_ucs.steps, 5)
        self.assertEqual(res_ucs.cost, 5)
        self.assertEqual(res_ucs.actions, ["S", "L", "L", "L", "N"])

        # A* com Manhattan também encontra a rota de custo ótimo (5)
        res_astar = astar(grid, manhattan)
        self.assertTrue(res_astar.found)
        self.assertEqual(res_astar.steps, 5)
        self.assertEqual(res_astar.cost, 5)
        self.assertEqual(res_astar.actions, ["S", "L", "L", "L", "N"])


if __name__ == "__main__":
    unittest.main()

