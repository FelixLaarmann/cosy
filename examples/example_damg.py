from typing import Iterable, Any, Union

from cosy import CoSy
from cosy.dsl import DSL
from cosy.types import Constructor, Group, Literal, Type, Var

class DAMGRepository:
    """
    A repository for directed acyclic multigraphs,
    following "An initial algebra approach to directed acyclic graphs" from Jeremy Gibbons.
    The following algebraic laws are defined on DAMGs (if we skip arguments,
    the variables are only the term arguments and the literals that are independent of the term arguments):

    beside(x, beside(y,z)) = beside(beside(x,y),z)  (associativity of beside)


    before(x, before(y,z)) = before(before(x,y),z)  (associativity of before)


    beside(before(m,n,p, w(m,n), x(n,p)), before(m',r,p', y(m',r), z(r,p')))
    =                                                                               (abiding law)
    before(m+m', n+r, p+p', beside(w(m,n),y(m',r)), beside(x(n,p),z(r,p')))


    swap(n, n, 0) and swap(n, 0, n) are neutral elements and therefore make no difference.

                                                                                                (swap simplification laws)

    before(besides(swap(m+n, m, n), copy(p,edge())), besides(copy(n, edge()), swap(m+p, m, p)))
    =
    swap(m + n + p, m, n+p)


    before(swap(m+n, m, n), before(beside(x(n,p), y(m,q)), swap(p+q, p, q)))
    =                                                                                 (swap law)
    beside(y(m,q),x(n,p))


    before(swap(m+n, m, n), swap(n+m, n, m)) = copy(m+n, edge())                  (simplified swap law)


    before(besides(copy(m, edge()), swap(n+p, n, p)), besides(swap(m+p, m, p), copy(n,edge())))
    =                                                                                            (derived simplification law)
    swap(m + n + p, m+n, p)

    before(edge(), x)
    =                                                                    (left neutrality of edge for before)
    x

    before(x, edge())
    =                                                                     (right neutrality of edge for before)
    x


    These laws will be interpreted as directed equalities, such that they correspond to the following
    term rewriting system:

    beside(beside(x,y),z)
    ->
    beside(x, beside(y,z))

    before(before(x,y),z)
    ->
    before(x, before(y,z))

    beside(before(m,n,p, w(m,n), x(n,p)), before(m',r,p', y(m',r), z(r,p')))
    ->
    before(m+m', n+r, p+p', beside(w(m,n),y(m',r)), beside(x(n,p),z(r,p')))

    before(besides(swap(m+n, m, n), copy(p,edge())), besides(copy(n, edge()), swap(m+p, m, p)))
    ->
    swap(m + n + p, m, n+p)

    before(swap(m+n, m, n), before(beside(x(n,p), y(m,q)), swap(p+q, p, q)))
    ->
    beside(y(m,q),x(n,p))

    before(swap(m+n, m, n), swap(n+m, n, m))
    ->
    copy(m+n, edge())

    before(besides(copy(m, edge()), swap(n+p, n, p)), besides(swap(m+p, m, p), copy(n,edge())))
    ->
    swap(m + n + p, m+n, p)

    before(edge(), x)
    ->
    x

    before(x, edge())
    ->
    x

    additionally any sequence of beside applied to the same term will be rewritten to copy this term to the length of this sequence:

    beside(x, beside(x,y))
    -> beside(copy(2, x), y)

    beside(copy(n, x), beside(copy(m, x), y))
    ->
    beside(copy(n+m, x), y)

    beside(x, x)
    ->
    copy(2, x)

    beside(copy(n, x), x)
    ->
    copy(n+1, x)

    beside(x, copy(n, x))
    ->
    copy(n+1, x)


    From our FSCD-paper "Restricting tree grammars with term rewriting systems" we know,
    that it should be sufficient to define a term-predicate that forbids all left-hand sides of the rules,
    to describe the set of combinatory terms, that are normal forms of the term rewriting system.
    """

    def __init__(self, dimension_upper_bound: int, labels: set[Any], dimension_lower_bound: int = 1):
        self.dimension_upper_bound: int = dimension_upper_bound
        self.dimension_lower_bound: int = dimension_lower_bound
        self.labels: set[Any] = labels

    class Dimension(Group):

        def __init__(self, dimension_upper_bound: int, dimension_lower_bound: int = 1):
            self.dimension_upper_bound: int = dimension_upper_bound
            self.dimension_lower_bound: int = dimension_lower_bound

        name = "dimension"

        def __iter__(self):
            yield from range(self.dimension_lower_bound, self.dimension_upper_bound + 1)

    def dimension(self):
        return self.Dimension(self.dimension_upper_bound, self.dimension_lower_bound)

    class Dimension_Matrix(Group):

        def __init__(self, dimension):
            self.Dimension = dimension

        name = "dimension_matrix"

        def __iter__(self):
            super().__iter__()

        def __contains__(self, item):
            return (isinstance(item, tuple)
                    and
                    all(
                        isinstance(t, tuple) and
                        all(isinstance(x, tuple) and
                            all((len(x) == 2, x[0] in self.Dimension(), x[1] in self.Dimension()))
                            for x in t)  # t is parallel composition of (input, output) pairs
                        for t in item  # item is sequential composition of parallel compositions
                    ) and
                    all(sum(map(lambda x: x[1], l)) == sum(map(lambda x: x[0], r)) for (l,r) in zip(item, item[1:]))
                    )   # output of one parallel composition must match input of the next

    def dimension_matrix(self):
        return self.Dimension_Matrix(self.dimension)

    class Label(Group):
        def __init__(self, label):
            self.labels = label

        name = "labels"

        def __iter__(self):
            yield from self.labels

    def label(self):
        return self.Label(self.labels)

    class Label_Matrix(Group):
        def __init__(self, label):
            self.labels = label

        name = "label_matrix"

        def __iter__(self):
            super().__iter__()

        def __contains__(self, item):
            return (isinstance(item, tuple) and
                    all(isinstance(t, tuple) and all(x in self.labels for x in t) for t in item))

    def label_matrix(self):
        return self.Label_Matrix(self.labels)

    class Swap_Matrix(Group):
        def __init__(self, dimension):
            self.Dimension = dimension

        name = "swap_matrix"

        def __iter__(self):
            super().__iter__()

        def __contains__(self, item):
            return (isinstance(item, tuple) and
                    all(isinstance(t, tuple) and
                        all(isinstance(x, tuple) and
                            (len(x) == 0 or
                             all((len(x) == 2, x[0] in self.Dimension(),
                                  x[0] != 0,
                                  x[1] in self.Dimension(),
                                  x[1] != 0 if len(t) == 1 else True)))
                            # swap 0 m -> swap m 0 and swap m 0 is neutral for sequential composition
                            for x in t)
                        for t in item) and
                    all(l[0][0] != r[0][1] and l[0][1] != r[0][0]
                        if len(l) == 1 == len(r) and len(l[0]) == 2 == len(r[0]) else True
                        for (l, r) in zip(item, item[1:])) and  #  simplified swap law: before(swap(m + n, m, n), swap(n + m, n, m))
                    all(all((l[1][1] != 0, r[0][1] != 0, l[0][0] != r[1][0], l[0][1] != r[0][0], l[1][0] != r[1][1]))
                        if len(l) == 2 == len(r) and all(len(x) == 2 for x in l + r) else True
                        for (l, r) in zip(item, item[1:])) and # swap simplification law: before(besides(swap(m + n, m, n), copy(p, edge())), besides(copy(n, edge()), swap(m + p, m, p)))
                    all(all((r[1][1] != 0, l[0][1] != 0, l[0][0] != r[0][0], l[1][0] != r[1][0], l[1][1] != r[0][1]))
                        if len(l) == 2 == len(r) and all(len(x) == 2 for x in l + r) else True
                        for (l, r) in zip(item, item[1:])) # derived simplification law: before(besides(copy(m, edge()), swap(n + p, n, p)), besides(swap(m + p, m, p), copy(n, edge())))
                    )

    def swap_matrix(self):
        return self.Swap_Matrix(self.dimension)

    def specification(self):
        return {
            "edge": Constructor("graph",
                                Constructor("input", Literal(1))
                                & Constructor("output", Literal(1))
                                & Constructor("dims", Literal((((1, 1),),)))
                                & Constructor("swaps", Literal((((1, 0),),)))
                                & Constructor("labels", Literal((((),),)))
                                ),
            "vertex": DSL()
            .parameter("m", self.dimension())
            .parameter("n", self.dimension())
            .parameter("d", self.dimension_matrix(), lambda v: [(((v["m"], v["n"]),),)])
            .parameter("l", self.label())
            .parameter("lm", self.label_matrix(), lambda v: [((v["l"],),)])
            .suffix(Constructor("graph",
                                Constructor("input", Var("m"))
                                & Constructor("output", Var("n"))
                                & Constructor("dims", Var("d"))
                                & Constructor("swaps", Literal((((),),)))
                                & Constructor("labels", Var("lm"))
                                )
                    ),

            "before": DSL()
            .parameter("d", self.dimension_matrix())
            .parameter_constraint(lambda v: len(v["d"]) > 1)  # abiding
            .parameter("mc", self.dimension_matrix(), lambda v: [v["d"][0:1]])  # before is right associative
            .parameter("cn", self.dimension_matrix(), lambda v: [v["d"][1:]])
            .parameter("m", self.dimension(), lambda v: [sum(x[0] for x in v["mc"])])
            .parameter("c", self.dimension(), lambda v: [sum(x[1] for x in v["mc"])])
            .parameter("n", self.dimension(), lambda v: [sum(x[0] for x in v["d"][-1])])
            .parameter("s", self.swap_matrix())
            .parameter_constraint(lambda v: len(v["d"]) == len(v["s"]))  # consistency of dims and swaps
            # .parameter_constraint(lambda v: len(v["s"]) > 1)  # abiding
            .parameter("smc", self.swap_matrix(), lambda v: [v["s"][0:1]])
            .parameter("scn", self.swap_matrix(), lambda v: [v["s"][1:]])
            .parameter_constraint(lambda v: all((v["smc"][0][0][0] != v["cn"][0][1][0],
                                                 v["smc"][0][0][1] != v["cn"][0][0][0],
                                                 v["cn"][0][0][1] != v["scn"][1][0][0],
                                                 v["cn"][0][1][1] != v["scn"][1][0][1]))
            if all((len(v["smc"]) == 1, len(v["scn"]) > 1, len(v["cn"][0]) == 2)) else True)   # len(v["scn"]) > 1 ~~> len(v["cn"]) > 1
            # swap law: before(swap(m + n, m, n), before(beside(x(n, p), y(m, q)), swap(p + q, p, q)))
            .parameter("l", self.label_matrix())
            .parameter_constraint(lambda v: len(v["d"]) == len(v["l"]))  # consistency of dims and labels
            .parameter("lmc", self.label_matrix(), lambda v: [v["l"][0]])
            .parameter("lcn", self.label_matrix(), lambda v: [v["l"][1:]])
            .argument("x", Constructor("graph",
                                Constructor("input", Var("m"))
                                & Constructor("output", Var("c"))
                                & Constructor("dims", Var("mc"))
                                & Constructor("swaps", Var("smc"))
                                & Constructor("labels", Var("lmc"))
                                )
                      )
            .argument("xs", Constructor("graph",
                                Constructor("input", Var("c"))
                                & Constructor("output", Var("n"))
                                & Constructor("dims", Var("cn"))
                                & Constructor("swaps", Var("scn"))
                                & Constructor("labels", Var("lcn"))
                                )
                      )
            .suffix(Constructor("graph",
                                Constructor("input", Var("m"))
                                & Constructor("output", Var("n"))
                                & Constructor("dims", Var("d"))
                                & Constructor("swaps", Var("s"))
                                & Constructor("labels", Var("l"))
                                )
                    ),

            """
            TODO add the following constraints to beside:
        - associativity of beside: beside(beside(x,y),z)
        - abiding law: beside(before(m,n,p, w(m,n), x(n,p)), before(m',r,p', y(m',r), z(r,p')))

        - enforce copy: beside(x, x)
        - enforce copy: beside(x, beside(x,y))
        - enforce copy: beside(copy(n, x), beside(copy(m, x), y))
        - enforce copy: beside(x, copy(n, x))
        - enforce copy: beside(copy(n, x), x)
            """: (),

            "beside": DSL()
            .parameter("d", self.dimension_matrix())
            .parameter_constraint(lambda v: len(v["d"]) > 1)  # abiding
            .parameter("mc", self.dimension_matrix())
            .parameter("cn", self.dimension_matrix())
            .parameter("m", self.dimension())
            .parameter("n", self.dimension())
            .parameter("p", self.dimension())
            .parameter("q", self.dimension())
            .parameter("q", self.dimension())
            .parameter("i", self.dimension(), lambda v: [v["m"] + v["p"]])
            .parameter("o", self.swap_matrix(), lambda v: [v["n"] + v["q"]])
            .parameter_constraint(lambda v: len(v["d"]) == len(v["s"]))  # consistency of dims and swaps
            .parameter("smc", self.swap_matrix())
            .parameter("scn", self.swap_matrix())
            .parameter("l", self.label_matrix())
            .parameter_constraint(lambda v: len(v["d"]) == len(v["l"]))  # consistency of dims and labels
            .parameter("lmc", self.label_matrix())
            .parameter("lcn", self.label_matrix())
            .argument("x", Constructor("graph",
                                Constructor("input", Var("m"))
                                & Constructor("output", Var("n"))
                                & Constructor("dims", Var("mc"))
                                & Constructor("swaps", Var("smc"))
                                & Constructor("labels", Var("lmc"))
                                )
                      )
            .argument("xs", Constructor("graph",
                                Constructor("input", Var("p"))
                                & Constructor("output", Var("q"))
                                & Constructor("dims", Var("cn"))
                                & Constructor("swaps", Var("scn"))
                                & Constructor("labels", Var("lcn"))
                                )
                      )
            .suffix(Constructor("graph",
                                Constructor("input", Var("i"))
                                & Constructor("output", Var("o"))
                                & Constructor("dims", Var("d"))
                                & Constructor("swaps", Var("s"))
                                & Constructor("labels", Var("l"))
                                )
                    ),


        }