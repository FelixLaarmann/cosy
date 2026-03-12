from src.cosy.core.tree import Tree
from src.cosy.core.types import Group, DataGroup
from src.cosy.core import SpecificationBuilder, Synthesizer, Constructor, Literal, Var
from src.cosy.core.solution_space import ConstantArgument

import time


class AVL_Repository:
    """
            Repository for AVL (binary search) trees (AVL-Tree) with string-labeled nodes
    """

    def __init__(self, max_height: int, labels: list[str]):
        self.max_height = max_height
        self.labels = labels

    @staticmethod
    def is_sorted(lst: list[str]) -> bool:
        sorted_lst = sorted(lst)
        return lst == sorted_lst


    def specification(self):
        heights = DataGroup("height", range(0, self.max_height + 1))
        labels = DataGroup("label", self.labels)

        return {
            "Node": SpecificationBuilder()
            .parameter("l", labels)
            .suffix(Constructor("AVL", Constructor("height", Literal(0)) & Constructor("height", Literal(None)) & Constructor("label", Var("l")) & Constructor("label", Literal(None)))),

            "Fork": SpecificationBuilder()
            .parameter("h1", heights)
            .parameter("h2", heights) #, lambda v: [v["h1"] - 1, v["h1"], v["h1"] + 1] if v["h1"] > 0 else [v["h1"], v["h1"] + 1]) # AVL balance condition
            .parameter("h", heights, lambda vs: [max(vs["h1"], vs["h2"]) + 1])
            .parameter_constraint(lambda v: v["h2"] - v["h1"] in [-1, 0, 1])  # AVL balance condition
            .parameter("l", labels)
            .argument("left", Constructor("AVL", Constructor("height", Var("h1")) & Constructor("label", Literal(None))))
            .argument("right", Constructor("AVL", Constructor("height", Var("h2")) & Constructor("label", Literal(None))))
            .constraint(lambda v: self.is_sorted(v["left"].interpret(self.inorder_traverse_algebra()) + [v["l"]] + v["right"].interpret(self.inorder_traverse_algebra())))
            .suffix(Constructor("AVL", Constructor("height", Var("h")) & Constructor("height", Literal(None)) & Constructor("label", Literal(None))))
        }

    def pretty_term_algebra(self):
        return {
            "Node": lambda l: f"Node ({l})",
            "Fork": lambda h1, h2, h, l, left, right: f"Fork ({l}) ({left}) ({right})"
        }

    def inorder_traverse_algebra(self):
        return {
            "Node": lambda l: [l],
            "Fork": lambda h1, h2, h, l, left, right: left + [l] + right
        }

class AVL_Bad_Repository:
    """
            Repository for AVL (binary search) trees (AVL-Tree) with string-labeled nodes
    """

    def __init__(self, max_height: int, labels: list[str]):
        self.max_height = max_height
        self.labels = labels

    @staticmethod
    def is_sorted(lst: list[str]) -> bool:
        sorted_lst = sorted(lst)
        return lst == sorted_lst


    def specification(self):
        heights = DataGroup("height", range(0, self.max_height + 1))
        labels = DataGroup("label", self.labels)

        return {
            "Node": SpecificationBuilder()
            .parameter("l", labels)
            .suffix(Constructor("AVL") & Constructor("height", Literal(0)) & Constructor("label", Var("l"))),

            "Fork": SpecificationBuilder()
            .parameter("h1", heights)
            .parameter("h2", heights) #, lambda v: [v["h1"] - 1, v["h1"], v["h1"] + 1] if v["h1"] > 0 else [v["h1"], v["h1"] + 1]) # AVL balance condition
            .parameter("h", heights, lambda v: [max(v["h1"], v["h2"]) + 1])
            .parameter_constraint(lambda v: v["h2"] - v["h1"] in [-1, 0, 1]) # AVL balance condition
            .parameter("l", labels)
            .argument("left", Constructor("AVL") & Constructor("height", Var("h1")))
            .argument("right", Constructor("AVL") & Constructor("height", Var("h2")))
            .constraint(lambda v: self.is_sorted(v["left"].interpret(self.inorder_traverse_algebra()) + [v["l"]] + v["right"].interpret(self.inorder_traverse_algebra())))
            .suffix(Constructor("AVL") & Constructor("height", Var("h")))
        }

    def pretty_term_algebra(self):
        return {
            "Node": lambda l: f"Node ({l})",
            "Fork": lambda h1, h2, h, l, left, right: f"Fork ({l}) ({left}) ({right})"
        }

    def inorder_traverse_algebra(self):
        return {
            "Node": lambda l: [l],
            "Fork": lambda h1, h2, h, l, left, right: left + [l] + right
        }





if __name__ == "__main__":

    repo = AVL_Repository(5, ["A", "B", "C"])

    target = Constructor("AVL", Constructor("height", Literal(None)) & Constructor("label", Literal(None)))
    synthesizer = Synthesizer(repo.specification(), {})

    start_time = time.time()
    solution_space = synthesizer.construct_solution_space(target).prune()
    end_time = time.time()

    print(f"SolutionSpace construction took {end_time - start_time:.5f} seconds.")

    """
    start_time = time.time()
    terms = solution_space.enumerate_trees(target, max_count=50)
    end_time = time.time()

    print(f"Term-Generator construction for enumeration took {end_time - start_time:.5f} seconds.")

    start_time = time.time()
    i = 0
    for term in terms:
        print(term.interpret(repo.pretty_term_algebra()))
        i += 1
    end_time = time.time()
    print(f"Enumeration, interpretation and printing of {i} terms took {end_time - start_time:.2f} seconds.")
    """
    print("Compare with bad repository:")

    repo_bad = AVL_Bad_Repository(5, ["A", "B", "C"])

    target_bad = Constructor("AVL")

    synthesizer_bad = Synthesizer(repo_bad.specification(), {})

    start_time = time.time()
    solution_space_bad = synthesizer_bad.construct_solution_space(target_bad).prune()
    end_time = time.time()

    print(f"SolutionSpace construction took {end_time - start_time:.5f} seconds.")

    bad_grammar = []
    for nt, rhss in solution_space_bad.as_tuples():
        for rhs in rhss:
            bad_grammar.append((nt, rhs))

    good_grammar = []
    for nt, rhss in solution_space.as_tuples():
        for rhs in rhss:
            good_grammar.append((nt, rhs))

    print(
        f"The bad repository leads to a solution space with {len(bad_grammar)} rules, while the proposed good repository leads to a solution space with {len(good_grammar)} rules.")

    for nt, rhs in bad_grammar:
        print(
            f"{nt} -> {rhs.terminal} {[str(arg.value) if isinstance(arg, ConstantArgument) else str(arg.origin) for arg in rhs.arguments]} with {len(rhs.predicates)} predicates:")
