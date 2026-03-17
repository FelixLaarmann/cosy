##Fibonacci##
"""
Overall description of this example goes here.
"""

from src.cosy.core.specification_builder import SpecificationBuilder
from src.cosy.core.types import Constructor, DataGroup, Literal, Type, Var, Arrow
from src.cosy.core.synthesizer import Synthesizer, Specification, Group
from src.cosy.core.solution_space import SolutionSpace, NonTerminalArgument, Goal, ConstantArgument
from src.cosy.core.tree import Tree
import time
from collections.abc import Callable, Iterable, Mapping
from itertools import product
from collections import deque



def main():
    solution_space = SolutionSpace()
    arguments = (ConstantArgument("x", 0, None),
                 NonTerminalArgument("v", "T1"),
                 ConstantArgument("y", 1, None),
                 NonTerminalArgument("w", "T1"),
                 NonTerminalArgument(None, "T1"),
                 ConstantArgument("z", 2, None),
                 NonTerminalArgument(None, "T1"))
    predicates = (lambda vs: vs["v"] == vs["w"],
                  lambda vs: vs["x"] == 0 and vs["y"] == 1 and vs["z"] == 2,)
    solution_space.add_rule("T0", "t", arguments, predicates)
    solution_space.add_rule("T1", "l", (), ())
    solution_space.add_rule("T1", "r", (), ())



    start_time = time.time()
    terms = solution_space.depth_first_resolution("T0", max_count=100)
    end_time = time.time()

    #start_time = time.time()
    #terms = solution_space.enumerate_trees("T0", max_count=100)
    #end_time = time.time()

    print(f"Term-Generator construction took {end_time - start_time:.5f} seconds.")

    trees = set()
    exptected_results = {
        "t 0 l 1 l l 2 l",
        "t 0 r 1 r r 2 r",
        "t 0 r 1 r r 2 l",
        "t 0 r 1 r l 2 r",
        "t 0 r 1 r l 2 l",
        "t 0 l 1 l r 2 r",
        "t 0 l 1 l r 2 l",
        "t 0 l 1 l l 2 r"
    }

    i = 0
    start_time = time.time()
    for tree in terms:
        trees.add(str(tree))
        print(tree)
        i += 1
    end_time = time.time()

    print(f"Enumeration and printing of {i} terms took {end_time - start_time:.2f} seconds.")

    print(f"All expected results are generated: {trees == exptected_results}")

if __name__ == "__main__":
    main()



