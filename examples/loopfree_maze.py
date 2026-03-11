##Fibonacci##
"""
Overall description of this example goes here.
"""

from src.cosy.core.specification_builder import SpecificationBuilder
from src.cosy.core.types import Constructor, DataGroup, Literal, Type, Var
from src.cosy.core.synthesizer import Synthesizer, Specification
from src.cosy.core.solution_space import SolutionSpace, NonTerminalArgument, Goal
from src.cosy.core.tree import Tree
import time
from collections.abc import Callable, Iterable, Mapping
from itertools import product
from collections import deque

def is_free(pos: tuple[int, int]) -> bool:
    col, row = pos
    seed = 0
    if row == col:
        return True
    return pow(11, (row + col + seed) * (row + col + seed) + col + 7, 1000003) % 5 > 0


def component_specifications() -> Mapping[
    Callable[[tuple[int, int], tuple[int, int], str], str] | str,
    Specification,
]:
    def up(b: tuple[int, int], _a: tuple[int, int], p: str) -> str:
        return f"{p} => UP({b})"

    def down(b: tuple[int, int], _a: tuple[int, int], p: str) -> str:
        return f"{p} => DOWN({b})"

    def left(b: tuple[int, int], _a: tuple[int, int], p: str) -> str:
        return f"{p} => LEFT({b})"

    def right(b: tuple[int, int], _a: tuple[int, int], p: str) -> str:
        return f"{p} => RIGHT({b})"

    def pos(ab: str) -> Type:
        return Constructor("pos", Var(ab))

    def getpath(path: Tree) -> Iterable[tuple[int, int]]:
        while path.root != "START":
            position = path.children[0].root
            path = path.children[2]
            if isinstance(position, tuple) and isinstance(path, Tree):
                yield position
            else:
                msg = "Expected position to be a tuple and path to be a tree."
                raise TypeError(msg)
        yield (0, 0)
        return

    int2 = DataGroup("int2", frozenset(filter(is_free, product(range(SIZE), range(SIZE)))))

    return {
        up: SpecificationBuilder()
        .parameter("b", int2)
        .parameter("a", int2, lambda vs: [(vs["b"][0], vs["b"][1] + 1)])
        .argument("pos", pos("a"))
        .constraint(lambda vs: vs["b"] not in getpath(vs["pos"]))
        .suffix(pos("b")),
        down: SpecificationBuilder()
        .parameter("b", int2)
        .parameter("a", int2, lambda vs: [(vs["b"][0], vs["b"][1] - 1)])
        .argument("pos", pos("a"))
        .constraint(lambda vs: vs["b"] not in getpath(vs["pos"]))
        .suffix(pos("b")),
        left: SpecificationBuilder()
        .parameter("b", int2)
        .parameter("a", int2, lambda vs: [(vs["b"][0] + 1, vs["b"][1])])
        .argument("pos", pos("a"))
        .constraint(lambda vs: vs["b"] not in getpath(vs["pos"]))
        .suffix(pos("b")),
        right: SpecificationBuilder()
        .parameter("b", int2)
        .parameter("a", int2, lambda vs: [(vs["b"][0] - 1, vs["b"][1])])
        .argument("pos", pos("a"))
        .constraint(lambda vs: vs["b"] not in getpath(vs["pos"]))
        .suffix(pos("b")),
        "START": "pos" @ (Literal((0, 0))),
    }


SIZE = 5

def euclidean_distance(pos1: tuple[int, int], pos2: tuple[int, int]) -> float:
    return ((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2) ** 0.5

def goal_weight(goal: Goal) -> float:
    if not goal.subgoals:
        return SIZE + 1.0
    max_len = max(len(p) for p in goal.subgoals.keys())
    filtered = filter(lambda x: len(x[0]) == max_len, goal.subgoals.items())
    distance = SIZE * SIZE + 1.0 # default weight if no subgoals are found in the goal, which is worse than any position in the grid

    for p, nt in filtered:
        if isinstance(nt.origin, Constructor):
            if nt.name == "pos":
                pos = nt.origin.arg
                if isinstance(pos, Literal) and isinstance(pos.value, tuple):
                    distance = euclidean_distance(pos.value, (0, 0)) # distance to START, because inhabitation works "backwards" from the target to the start
    return distance

Path = tuple[int, ...]

def main():
    synthesizer = Synthesizer(component_specifications(), {})

    target: Type = "pos" @ (Literal((SIZE - 1, SIZE - 1)))

    def variance_strategy_push(queue: deque[Goal], new_goals: Iterable[Goal]) -> deque[Goal]:
        filtered = list(filter(lambda g: len(g.subgoals) <= SIZE * SIZE,
                               new_goals))  # there can be no loop-free path longer than SIZE * SIZE in a SIZE x SIZE grid
        all = list(queue) + filtered
        all_sorted = sorted(all, key=lambda g: goal_weight(g))  # sort the whole queue by the weight of the goals, so that the best goal is always at the front of the queue
        return deque(all_sorted)


    def variance_strategy_pop(queue: deque[Goal]) -> tuple[deque[Goal], Goal]:
        return queue, queue.popleft()  # depth-first search <~> LIFO


    def goal_selection_strategy(goal: Goal) -> tuple[Path, NonTerminalArgument[Type]]:
        max_len = max(len(p) for p in goal.subgoals.keys())
        filtered = filter(lambda x: len(x[0]) == max_len, goal.subgoals.items())
        return min(filtered, key=lambda item: item[0][-1])  # leftmost selection, assuming new subgoals (deeper positions) are added "to the left" of the old ones

    start_time = time.time()
    solution_space = synthesizer.construct_solution_space(target).prune()
    end_time = time.time()

    print(f"SolutionSpace construction took {end_time - start_time:.5f} seconds.")
    """
    start_time = time.time()
    terms = solution_space.breadth_first_resolution(target, max_count=5)
    end_time = time.time()
    """
    start_time = time.time()
    # greedy best-first search with custom variance strategies and goal selection strategy
    terms = solution_space.resolution(target, max_count=2,
                                      variance_strategy_push=variance_strategy_push,
                                      variance_strategy_pop=variance_strategy_pop,
                                      goal_selection_strategy=goal_selection_strategy)
    end_time = time.time()
    #"""
    #start_time = time.time()
    #terms = solution_space.enumerate_trees(target, max_count=5)
    #end_time = time.time()

    print(f"Term-Generator construction took {end_time - start_time:.5f} seconds.")

    start_time = time.time()
    i = 0
    for term in terms:
        print(term.interpret())
        i += 1
    end_time = time.time()
    print(f"Enumeration and printing of {i} terms took {end_time - start_time:.2f} seconds.")

    """
    solution_space = SolutionSpace()
    width = 20
    solution_space.add_rule("Tree0", "t0", (NonTerminalArgument(None, "Tree1"),), ())
    solution_space.add_rule("Tree1", "t1", tuple(NonTerminalArgument(None, "Tree2") for _ in range(width)), ())
    solution_space.add_rule("Tree2", "t2", (NonTerminalArgument(None, "Tree3"),), ())
    solution_space.add_rule("Tree3", "t3", tuple(NonTerminalArgument(None, "Tree4") for _ in range(width)), ())
    solution_space.add_rule("Tree4", "t4_l", (), ())
    solution_space.add_rule("Tree4", "t4_r", (), ())

    start_time = time.time()
    terms = solution_space.depth_first_resolution("Tree0", max_count=10)
    end_time = time.time()

    print(f"Term-Generator construction took {end_time - start_time:.5f} seconds.")

    start_time = time.time()
    i = 0
    for term in terms:
        print(term)
        i += 1
    end_time = time.time()
    print(f"Enumeration and printing of {i} terms took {end_time - start_time:.2f} seconds.")
    """
if __name__ == "__main__":
    main()


