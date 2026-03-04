##Fibonacci##
"""
Overall description of this example goes here.
"""

from src.cosy.core.specification_builder import SpecificationBuilder
from src.cosy.core.types import Constructor, DataGroup, Literal, Type, Var
from src.cosy.core.synthesizer import Synthesizer, Specification
from src.cosy.core.solution_space import SolutionSpace, NonTerminalArgument
from src.cosy.core.tree import Tree
import time
from collections.abc import Callable, Iterable, Mapping
from itertools import product

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


SIZE = 3

def main():
    synthesizer = Synthesizer(component_specifications(), {})

    target: Type = "pos" @ (Literal((SIZE - 1, SIZE - 1)))
    #target: Type = Constructor("fib") & Constructor("at", Literal(22))

    start_time = time.time()
    solution_space = synthesizer.construct_solution_space(target).prune()
    end_time = time.time()

    print(f"SolutionSpace construction took {end_time - start_time:.5f} seconds.")

    start_time = time.time()
    terms = solution_space.breadth_first_resolution(target, max_count=3)
    end_time = time.time()

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


