import heapq
from collections import deque
from collections.abc import Callable

from .models import SearchResult
from .problem import WeightedGrid, DIRECTIONS, Pos, CELL_COST, ALLOWED

Heuristic = Callable[[tuple[int, int], tuple[int, int]], float]


def bfs(problem: WeightedGrid) -> SearchResult:
    """Busca em Largura. Implemente conforme a especificação do trabalho."""

    start = problem.start
    goal = problem.goal

    visited: set[Pos] = {start}
    queue = deque([start])
    came_from: dict[Pos, tuple[Pos | None, str | None, int]] = {}

    came_from[problem.start] = (None, None, 0)

    found = False
    generated = 1
    expanded = 0
    peak_frontier = 1
    peak_stored_states = 1

    while len(queue) > 0:
        peak_frontier = max(peak_frontier, len(queue))
        peak_stored_states = max(peak_stored_states, len(visited))

        currentPos = queue.popleft()

        if problem.goal_test(currentPos):
            # found goal
            found = True
            break

        expanded += 1

        for action, nxt, step_cost in problem.successors(currentPos):
            if nxt not in visited:
                visited.add(nxt)
                came_from[nxt] = (currentPos, action, step_cost)
                queue.append(nxt)
                generated += 1
                peak_frontier = max(peak_frontier, len(queue))
                peak_stored_states = max(peak_stored_states, len(visited))

    if not found:
        return SearchResult(
            found=False,
            algorithm="bfs",
            generated=generated,
            expanded=expanded,
            peak_frontier=peak_frontier,
            peak_stored_states=peak_stored_states,
        )

    path = []
    actions = []
    currentPos = goal
    cost = 0

    while currentPos is not None:
        path.append(currentPos)
        parent, act, step_cost = came_from[currentPos]
        if act is not None:
            actions.append(act)
            cost += step_cost
        currentPos = parent

    path.reverse()
    actions.reverse()

    return SearchResult(
        found,
        "bfs",
        path,
        actions,
        cost,
        generated,
        expanded,
        peak_frontier,
        peak_stored_states,
    )


def dfs(problem: WeightedGrid) -> SearchResult:
    """Busca em Profundidade. Implemente conforme a especificação do trabalho."""

    start = problem.start
    goal = problem.goal

    visited: set[Pos] = {start}
    stack: list[Pos] = [start]
    came_from: dict[Pos, tuple[Pos | None, str | None, int]] = {}

    came_from[problem.start] = (None, None, 0)

    found = False
    generated = 1
    expanded = 0
    peak_frontier = 1
    peak_stored_states = 1

    while len(stack) > 0:
        peak_frontier = max(peak_frontier, len(stack))
        peak_stored_states = max(peak_stored_states, len(visited))

        currentPos = stack.pop()

        if problem.goal_test(currentPos):
            found = True
            break

        expanded += 1

        # Para que a ordem efetiva de expansão seja N -> L -> S -> O,
        # empilhamos os sucessores na ordem reversa.
        for action, nxt, step_cost in reversed(list(problem.successors(currentPos))):
            if nxt not in visited:
                visited.add(nxt)
                came_from[nxt] = (currentPos, action, step_cost)
                stack.append(nxt)
                generated += 1
                peak_frontier = max(peak_frontier, len(stack))
                peak_stored_states = max(peak_stored_states, len(visited))

    if not found:
        return SearchResult(
            found=False,
            algorithm="dfs",
            generated=generated,
            expanded=expanded,
            peak_frontier=peak_frontier,
            peak_stored_states=peak_stored_states,
        )

    path = []
    actions = []
    currentPos = goal
    cost = 0

    while currentPos is not None:
        path.append(currentPos)
        parent, act, step_cost = came_from[currentPos]
        if act is not None:
            actions.append(act)
            cost += step_cost
        currentPos = parent

    path.reverse()
    actions.reverse()

    return SearchResult(
        found,
        "dfs",
        path,
        actions,
        cost,
        generated,
        expanded,
        peak_frontier,
        peak_stored_states,
    )


def uniform_cost(problem: WeightedGrid) -> SearchResult:
    """Busca de Custo Uniforme. Implemente conforme a especificação do trabalho."""

    start = problem.start
    goal = problem.goal

    counter = 0
    # heap armazena: (g(n), ordem_insercao, pos)
    heap: list[tuple[int, int, Pos]] = [(0, counter, start)]
    cost_so_far: dict[Pos, int] = {start: 0}
    came_from: dict[Pos, tuple[Pos | None, str | None, int]] = {}
    came_from[start] = (None, None, 0)

    explored: set[Pos] = set()
    frontier_counts: dict[Pos, int] = {start: 1}

    found = False
    generated = 1
    expanded = 0
    peak_frontier = 1
    peak_stored_states = 1

    while len(heap) > 0:
        g, _, currentPos = heapq.heappop(heap)
        frontier_counts[currentPos] -= 1
        if frontier_counts[currentPos] == 0:
            del frontier_counts[currentPos]

        # Entradas obsoletas da fila de prioridade devem ser ignoradas
        if currentPos in explored:
            continue
        if g > cost_so_far[currentPos]:
            continue

        if problem.goal_test(currentPos):
            found = True
            break

        explored.add(currentPos)
        expanded += 1

        for action, nxt, step_cost in problem.successors(currentPos):
            new_cost = g + step_cost
            if nxt not in cost_so_far or new_cost < cost_so_far[nxt]:
                cost_so_far[nxt] = new_cost
                came_from[nxt] = (currentPos, action, step_cost)
                counter += 1
                heapq.heappush(heap, (new_cost, counter, nxt))
                generated += 1
                frontier_counts[nxt] = frontier_counts.get(nxt, 0) + 1
                if nxt in explored:
                    explored.remove(nxt)

                peak_frontier = max(peak_frontier, len(frontier_counts))
                peak_stored_states = max(
                    peak_stored_states, len(set(frontier_counts.keys()) | explored)
                )

    if not found:
        return SearchResult(
            found=False,
            algorithm="ucs",
            generated=generated,
            expanded=expanded,
            peak_frontier=peak_frontier,
            peak_stored_states=peak_stored_states,
        )

    path = []
    actions = []
    currentPos = goal
    cost = cost_so_far[goal]

    while currentPos is not None:
        path.append(currentPos)
        parent, act, _ = came_from[currentPos]
        if act is not None:
            actions.append(act)
        currentPos = parent

    path.reverse()
    actions.reverse()

    return SearchResult(
        found,
        "ucs",
        path,
        actions,
        cost,
        generated,
        expanded,
        peak_frontier,
        peak_stored_states,
    )


def greedy(problem: WeightedGrid, heuristic: Heuristic) -> SearchResult:
    """Busca Gulosa pelo melhor primeiro."""

    start = problem.start
    goal = problem.goal

    counter = 0
    h_start = heuristic(start, goal)
    # heap armazena: (h(n), ordem_insercao, pos)
    heap: list[tuple[float, int, Pos]] = [(h_start, counter, start)]
    came_from: dict[Pos, tuple[Pos | None, str | None, int]] = {}
    came_from[start] = (None, None, 0)

    visited: set[Pos] = {start}
    frontier_counts: dict[Pos, int] = {start: 1}

    found = False
    generated = 1
    expanded = 0
    peak_frontier = 1
    peak_stored_states = 1

    while len(heap) > 0:
        h, _, currentPos = heapq.heappop(heap)
        frontier_counts[currentPos] -= 1
        if frontier_counts[currentPos] == 0:
            del frontier_counts[currentPos]

        if problem.goal_test(currentPos):
            found = True
            break

        expanded += 1

        for action, nxt, step_cost in problem.successors(currentPos):
            if nxt not in visited:
                visited.add(nxt)
                came_from[nxt] = (currentPos, action, step_cost)
                counter += 1
                h_nxt = heuristic(nxt, goal)
                heapq.heappush(heap, (h_nxt, counter, nxt))
                generated += 1
                frontier_counts[nxt] = frontier_counts.get(nxt, 0) + 1
                peak_frontier = max(peak_frontier, len(frontier_counts))
                peak_stored_states = max(peak_stored_states, len(visited))

    if not found:
        return SearchResult(
            found=False,
            algorithm="greedy",
            generated=generated,
            expanded=expanded,
            peak_frontier=peak_frontier,
            peak_stored_states=peak_stored_states,
        )

    path = []
    actions = []
    currentPos = goal
    cost = 0

    while currentPos is not None:
        path.append(currentPos)
        parent, act, step_cost = came_from[currentPos]
        if act is not None:
            actions.append(act)
            cost += step_cost
        currentPos = parent

    path.reverse()
    actions.reverse()

    return SearchResult(
        found,
        "greedy",
        path,
        actions,
        cost,
        generated,
        expanded,
        peak_frontier,
        peak_stored_states,
    )


def astar(problem: WeightedGrid, heuristic: Heuristic) -> SearchResult:
    """Busca A*."""

    start = problem.start
    goal = problem.goal

    counter = 0
    h_start = heuristic(start, goal)
    # heap armazena: (f(n), h(n), ordem_insercao, pos)
    heap: list[tuple[float, float, int, Pos]] = [(h_start, h_start, counter, start)]
    cost_so_far: dict[Pos, int] = {start: 0}
    came_from: dict[Pos, tuple[Pos | None, str | None, int]] = {}
    came_from[start] = (None, None, 0)

    explored: set[Pos] = set()
    frontier_counts: dict[Pos, int] = {start: 1}

    found = False
    generated = 1
    expanded = 0
    peak_frontier = 1
    peak_stored_states = 1

    while len(heap) > 0:
        f, h, _, currentPos = heapq.heappop(heap)
        frontier_counts[currentPos] -= 1
        if frontier_counts[currentPos] == 0:
            del frontier_counts[currentPos]

        # Entradas obsoletas da fila de prioridade devem ser ignoradas
        if currentPos in explored:
            continue
        g = f - h
        if g > cost_so_far[currentPos]:
            continue

        if problem.goal_test(currentPos):
            found = True
            break

        explored.add(currentPos)
        expanded += 1

        for action, nxt, step_cost in problem.successors(currentPos):
            new_cost = cost_so_far[currentPos] + step_cost
            if nxt not in cost_so_far or new_cost < cost_so_far[nxt]:
                cost_so_far[nxt] = new_cost
                came_from[nxt] = (currentPos, action, step_cost)
                counter += 1
                h_nxt = heuristic(nxt, goal)
                f_nxt = new_cost + h_nxt
                heapq.heappush(heap, (f_nxt, h_nxt, counter, nxt))
                generated += 1
                frontier_counts[nxt] = frontier_counts.get(nxt, 0) + 1
                if nxt in explored:
                    explored.remove(nxt)

                peak_frontier = max(peak_frontier, len(frontier_counts))
                peak_stored_states = max(
                    peak_stored_states, len(set(frontier_counts.keys()) | explored)
                )

    if not found:
        return SearchResult(
            found=False,
            algorithm="astar",
            generated=generated,
            expanded=expanded,
            peak_frontier=peak_frontier,
            peak_stored_states=peak_stored_states,
        )

    path = []
    actions = []
    currentPos = goal
    cost = cost_so_far[goal]

    while currentPos is not None:
        path.append(currentPos)
        parent, act, _ = came_from[currentPos]
        if act is not None:
            actions.append(act)
        currentPos = parent

    path.reverse()
    actions.reverse()

    return SearchResult(
        found,
        "astar",
        path,
        actions,
        cost,
        generated,
        expanded,
        peak_frontier,
        peak_stored_states,
    )

