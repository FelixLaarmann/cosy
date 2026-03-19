##Fibonacci##
"""
Overall description of this example goes here.
"""

from src.cosy.core.specification_builder import SpecificationBuilder
from src.cosy.core.types import Constructor, DataGroup, Literal, Type, Var
from src.cosy.core.synthesizer import Synthesizer
from src.cosy.core.solution_space import SolutionSpace, NonTerminalArgument
import time


def fib_zero() -> int:
    """
    The Fibonacci number at index 0.

    :return: The Fibonacci number at index 0.
    """
    return 0


def fib_one() -> int:
    """
    The Fibonacci number at index .

    :return: The Fibonacci number at index 1.
    """
    return 1


def fib_next(_z: int, _y: int, _x: int, f1: int, f2: int) -> int:
    """
    Calculate the Fibonacci number at a given index z using the Fibonacci numbers
    at indices x = z - 2 and y = z - 1.

    :param _z: The index for which the Fibonacci number is calculated.
    :param _y: The index z - 1.
    :param _x: The index z - 2.
    :param f1: The Fibonacci number at index (z - 1).
    :param f2: The Fibonacci number at index (z - 2).
    :return: The Fibonacci number at index z.
    """
    return f1 + f2


def main():
    # range of relevant indices for Fibonacci numbers
    bound = 15

    named_components_with_specifications = [
        (  #
            "fib_zero",
            fib_zero,
            SpecificationBuilder().suffix(Constructor("fib") & Constructor("at", Literal(0))),
        ),
        (  #
            "fib_one",
            fib_one,
            SpecificationBuilder().suffix(Constructor("fib") & Constructor("at", Literal(1))),
        ),
        (  #
            "fib_next",
            fib_next,
            SpecificationBuilder()
            .parameter("z", DataGroup("int", range(bound)))
            .parameter("y", DataGroup("int", range(bound)), lambda vs: [vs["z"] - 1])
            .parameter("x", DataGroup("int", range(bound)), lambda vs: [vs["z"] - 2])
            .argument("f1", Constructor("fib") & Constructor("at", Var("y")))
            .argument("f2", Constructor("fib") & Constructor("at", Var("x")))
            .suffix(Constructor("fib") & Constructor("at", Var("z"))),
        ),
    ]

    component_specifications = {
        name: specification for name, _, specification in named_components_with_specifications
    }

    component_interpretations = {
        name: interpretation for name, interpretation, _ in named_components_with_specifications
    }

    synthesizer = Synthesizer(component_specifications, {})

    target: Type = Constructor("fib")
    #target: Type = Constructor("fib") & Constructor("at", Literal(22))

    start_time = time.time()
    solution_space = synthesizer.construct_solution_space(target).prune()
    end_time = time.time()

    print(f"SolutionSpace construction took {end_time - start_time:.5f} seconds.")

    start_time = time.time()
    terms = solution_space.sample(target, 10)
    end_time = time.time()

    print(f"Term-Generator construction took {end_time - start_time:.5f} seconds.")

    start_time = time.time()
    i = 0
    for term in terms:
        print(term.interpret(component_interpretations))
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


