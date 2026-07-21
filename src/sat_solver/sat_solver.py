from sat_solver.ext_class import ZeroClass, Undefined, ExtClass
from sat_solver.differential import Differential
from sat_solver.ext import Ext
from sat_solver.literal_manager import LiteralManager
from pysat.solvers import Solver
from pysat.formula import And, Implies, Neg, Formula
from pysat.card import CardEnc


class SATSolver:
    E1_page: Ext
    literal_manager: LiteralManager
    max_differential: int
    known_differentials: dict[tuple[ExtClass, int], ExtClass]

    def __init__(self, E1_page: Ext, max_differential: int):
        self.E1_page = E1_page
        self.literal_manager = LiteralManager()
        self.max_differential = max_differential
        known_diffs = self.E1_page.get_known_differentials()
        self.known_differentials = {}
        for differential in known_diffs:
            source = differential.get_source()
            degree = differential.get_degree()
            target = differential.get_target()
            self.known_differentials[(source, degree)] = target


    #this function creates the variables for the SAT solver.
    def create_literals(self):
        classes = self.E1_page.get_classes()
        for ext_class in classes:
            print(
                f"Creating literals with source {ext_class.get_degree()}, {ext_class.get_vector()}"
            )
            for r in self.E1_page.r_with_nonzero_target(ext_class.get_degree()):
                target_classes = [ZeroClass, Undefined]
                target_classes += self.E1_page.get_possible_differential_targets(
                    ext_class, r
                )
                for target_class in target_classes:
                    #print(
                    #    f"Creating differential literal: ({ext_class.tridegree}, {ext_class.vector})--d{r}--> ({target_class.tridegree}, {target_class.vector})"
                    #)
                    differential = Differential(ext_class, target_class, r)
                    self.literal_manager.add_differential(differential)
        for r in range(1, self.max_differential + 1):
            #print(f"Creating differential literal: (None, [True])--d{r}--> (None, [True])")
            self.literal_manager.add_differential(Differential(ZeroClass, ZeroClass, r))
            #print(f"Creating differential literal: (None, [False])--d{r}--> (None, [False])")
            self.literal_manager.add_differential(Differential(Undefined, Undefined, r))


    def create_known_differential_clauses(self) -> list[int]:
        """
        This creates the composite clause that enforces the known differentials in the SAT solver.

        Returns:
            list[int]: A list of integers representing the literals we are assuming to be true

        Raises:
            ValueError: If a known differential is not found in the literal manager.
        """
        knowns = []
        for (source, degree), target in self.known_differentials.items():
#            print(
#                f"Adding known differential: ({source.tridegree}, {source.vector}) --d{degree}--> ({target.tridegree}, {target.vector})"
#            )
            differential = Differential(source, target, degree)
            atom = self.literal_manager.get_differential_atom(differential)
            if atom is not None:
                knowns.append(atom)
            else:
                raise ValueError(
                    f"Known differential {differential} not found in literal manager."
                )

        # d_r(0) = 0, d_r(Undef) = Undef are always true
        for r in range(1, self.max_differential + 1):
            zero_differential = Differential(ZeroClass, ZeroClass, r)
            zero_atom = self.literal_manager.get_differential_atom(zero_differential)
            if zero_atom is not None:
                knowns.append(zero_atom)
            else:
                raise ValueError(
                    f"Zero differential {zero_differential} not found in literal manager."
                )

            undefined_differential = Differential(Undefined, Undefined, r)
            undefined_atom = self.literal_manager.get_differential_atom(
                undefined_differential
            )
            if undefined_atom is not None:
                knowns.append(undefined_atom)
            else:
                raise ValueError(
                    f"Undefined differential {undefined_differential} not found in literal manager."
                )

        return [known.name for known in knowns]

    def create_leibniz_differentials(
        self, diff1: Differential, diff2: Differential
    ) -> Differential:
        """
        Given two differential questions, this creates the differential question that represents the Leibniz rule applied to these two differentials.

        Args:
            diff1 (Differential): The first differential question.
            diff2 (Differential): The second differential question.

        Returns:
            Differential: A differential question representing the Leibniz rule applied to the two input differentials.

        Raises:
            ValueError: If the two differentials do not have the same degree or if the target of either differential is Undefined.
        """
        if diff1.get_degree() != diff2.get_degree():
            raise ValueError(
                f"Differentials {diff1} and {diff2} do not have the same degree."
            )
        source1 = diff1.get_source()
        source2 = diff2.get_source()
        target1 = diff1.get_target()
        target2 = diff2.get_target()
        if target1 == Undefined or target2 == Undefined:
            raise ValueError(
                f"Differentials {diff1} and {diff2} have Undefined targets, which is not allowed for Leibniz differentials."
            )

        leibniz_source = source1 * source2
        leibniz_target = target1 * source2 + source1 * target2

        return Differential(leibniz_source, leibniz_target, diff1.get_degree())

    def create_linearity_differential(
        self, diff1: Differential, diff2: Differential
    ) -> Differential:
        """
        Given two differential questions, this creates the differential question that represents the linearity rule applied to these two differentials.

        Args:
            diff1 (Differential): The first differential question.
            diff2 (Differential): The second differential question.

        Returns:
            Differential: A differential question representing the linearity rule applied to the two input differentials.

        Raises:
            ValueError: If the two differentials do not have the same degree or if their sources are not in the same tridegree or if the targets of either differential are Undefined.
        """
        if diff1.get_degree() != diff2.get_degree():
            raise ValueError(
                f"Differentials {diff1} and {diff2} do not have the same degree."
            )
        source1 = diff1.get_source()
        source2 = diff2.get_source()
        target1 = diff1.get_target()
        target2 = diff2.get_target()

        if not source1.in_same_tridegree_as(source2):
            raise ValueError(
                f"Differentials {diff1} and {diff2} do not have sources in the same tridegree."
            )
        if target1 == Undefined or target2 == Undefined:
            raise ValueError(
                f"Differentials {diff1} and {diff2} have Undefined targets, which is not allowed for linearity differentials."
            )

        linearity_source = source1 + source2
        linearity_target = target1 + target2

        return Differential(linearity_source, linearity_target, diff1.get_degree())

    """
    I'm leaving this commented out for when we go back to the Leibniz rule, but
    for now we can avoid iterating over all pairs of differentials (VERY slow)
    """

#    def create_clauses_from_assumed_differential(self, diff: Differential) -> Formula:
#        """
#        Given a differential question, this creates the clauses that enforce the Leibniz, linearity, and square-zero rules for this differential
#        via implications.

#        Args:
#            diff (Differential): The differential question.

#        Returns:
#            Formula: A formula representing the implications of the Leibniz, linearity, and square-zero rules for the differential.

#        Raises:
#            ValueError: If the differential is not found in the literal manager.
#            Errors raised by the Leibniz, linearity, or square-zero clause creation methods.
#        """
#        antecedent = self.literal_manager.get_differential_atom(diff)
#        conditional_consequents = []

#        source = diff.get_source()
#        source_degree = source.get_degree()
#        degree = diff.get_degree()
#        target = diff.get_target()

#        for other_class in self.E1_page.get_classes():
#            other_deg = other_class.get_degree()
#            # Multiplication is commutative, choose only one of a * b, b * a
#            if other_deg < source_degree:
#                continue
#            target_classes = [ZeroClass]
#            target_classes += self.E1_page.get_possible_differential_targets(
#                other_class, degree
#            )
#            for target_class in target_classes:
#                other_diff = Differential(other_class, target_class, degree)
#                other_antecedent = self.literal_manager.get_differential_atom(
#                    other_diff
#                )
#                other_consequents = []

#                # TODO: Implement multiplication and reenable this
#                # leibniz_diff = self.create_leibniz_differentials(diff, other_diff)
#                # diff_source = leibniz_diff.get_source()
#                # diff_target = leibniz_diff.get_target()
#                # if (
#                #     diff_source.get_coweight() <= self.max_coweight
#                #     and diff_target.get_coweight() <= self.max_coweight
#                # ):
#                #     leibniz_consequent = self.literal_manager.get_differential_atom(
#                #         leibniz_diff
#                #     )
#                #     if leibniz_consequent is not None:
#                #         other_consequents.append(leibniz_consequent)
#                #     else:
#                #         raise ValueError(
#                #             f"Leibniz differential {leibniz_diff} not found in literal manager."
#                #         )

#                #This is for linearity.
#                if (
#                    source.in_same_tridegree_as(other_class)
#                    and source != other_class
#                    and target != Undefined
#                    and target_class != Undefined
#                ):
#                    linearity_diff = self.create_linearity_differential(
#                        diff, other_diff
#                    )
##                    print(
##                        f"Creating linearity differential: {linearity_diff.get_source().tridegree}, {linearity_diff.get_source().vector} --d{linearity_diff.get_degree()}--> {linearity_diff.get_target().tridegree}, {linearity_diff.get_target().vector}"
##                    )
#                    linearity_consequent = self.literal_manager.get_differential_atom(
#                        linearity_diff
#                    )
#                    if linearity_consequent is not None:
#                        other_consequents.append(linearity_consequent)
#                    else:
#                        raise ValueError(
#                            f"Linearity differential {linearity_diff.get_source().tridegree}, {linearity_diff.get_source().vector} --d{linearity_diff.get_degree()}--> {linearity_diff.get_target().tridegree}, {linearity_diff.get_target().vector} not found in literal manager."
#                        )

#                if other_consequents:
#                    other_consequent = And(*other_consequents)
#                    conditional_consequents.append(
#                        Implies(other_antecedent, other_consequent)
#                    )

#        # if d_r(x) = y then d_r(y) = 0
#        if target != Undefined:
#            square_zero_diff = Differential(target, ZeroClass, degree)
#            square_zero_consequent = self.literal_manager.get_differential_atom(
#                square_zero_diff
#            )
#            if square_zero_consequent is not None:
#                conditional_consequents.append(square_zero_consequent)
#            else:
#                raise ValueError(
#                    f"Square-zero differential {square_zero_diff} not found in literal manager."
#                )

#        if len(conditional_consequents) > 0:
#            consequent = And(*conditional_consequents)
#            return Implies(antecedent, consequent)
#        else:
#            return None


    def create_linearity_and_square0_clauses(self, diff: Differential) -> Formula:
        """
        Given a differential question, this creates the clauses that enforce the linearity and square zero (i.e., d^2 = 0) clauses for this differential via implications.

        Args:
            diff (Differential): The differential question.

        Returns:
            Formula: A formula representing the implications of the linearity and square zero rules for the differential.

        Raises:
            ValueError: If the differential is not found in the literal manager.
            Errors raised by the linearity and square zero clause creation methods.
        """
        antecedent = self.literal_manager.get_differential_atom(diff)
        conditional_consequents = []

        source = diff.get_source()
        source_degree = source.get_degree()
        degree = diff.get_degree()
        target = diff.get_target()
        if target == Undefined:
            return None

        # FIXME: this double-counts pairs of differentials to add
        for other_class in self.E1_page.get_nonzero_classes_in_tridegree(source_degree):
            if other_class == source:
                continue
            target_classes = [ZeroClass]
            target_classes += self.E1_page.get_possible_differential_targets(
                other_class, degree
            )
            for target_class in target_classes:
                other_diff = Differential(other_class, target_class, degree)
                other_diff_atom = self.literal_manager.get_differential_atom(
                    other_diff
                )

                linearity_diff = self.create_linearity_differential(
                    diff, other_diff
                )
                print(
                    f"Creating linearity differential: {linearity_diff.get_source().tridegree}, {linearity_diff.get_source().vector} --d{linearity_diff.get_degree()}--> {linearity_diff.get_target().tridegree}, {linearity_diff.get_target().vector}"
                )
                linearity_consequent = self.literal_manager.get_differential_atom(
                    linearity_diff
                )
                if linearity_consequent is not None:
                    conditional_consequents.append(
                        Implies(other_diff_atom, linearity_consequent)
                    )
                else:
                    raise ValueError(
                        f"Linearity differential {linearity_diff.get_source().tridegree}, {linearity_diff.get_source().vector} --d{linearity_diff.get_degree()}--> {linearity_diff.get_target().tridegree}, {linearity_diff.get_target().vector} not found in literal manager."
                    )

        if target != ZeroClass:
            # if d_r(x) = y then d_{r'}(y) = 0 for all r'
            for r1 in self.E1_page.r_with_nonzero_target(target.get_degree()):
                square_zero_diff = Differential(target, ZeroClass, r1)
                square_zero_consequent = self.literal_manager.get_differential_atom(
                    square_zero_diff
                )
                if square_zero_consequent is not None:
                    conditional_consequents.append(square_zero_consequent)
                else:
                    raise ValueError(
                        f"Square-zero differential {square_zero_diff} not found in literal manager."
                    )
            # if d_r(x) = y then d_{r'}(z) != y for any r' > r
            for r1 in self.E1_page.r_with_nonzero_source(target.get_degree()):
                if r1 <= degree:
                    continue
                for z in self.E1_page.get_possible_nontrivial_differential_sources(target, r1):
                    w_src = z.get_degree()[2]
                    w_tgt = target.get_degree()[2]
                    r1 = w_tgt - w_src
                    higher_diff = Differential(z, target, r1)
                    higher_diff_atom = self.literal_manager.get_differential_atom(higher_diff)
                    neg_clause = Neg(higher_diff_atom)
                    conditional_consequents.append(neg_clause)

        if len(conditional_consequents) > 0:
            consequent = And(*conditional_consequents)
            return Implies(antecedent, consequent)
        else:
            return None


    def run_sat_solver(self):
        """
        This method constructs literals and constraints for the SAT solver based on the E1 page, known differentials, and the Leibniz, linearity, and square-zero rules.
        Satisfiability is tested and models are enumerated.
        """
        self.create_literals()
        known_clauses = self.create_known_differential_clauses()
        all_clauses = []
        cardinality_constraints = []
        for source in self.E1_page.get_classes():
            for r in self.E1_page.r_with_nonzero_target(source.get_degree()):
                target_classes = [ZeroClass, Undefined]
                target_classes += self.E1_page.get_possible_differential_targets(
                    source, r
                )
                equals_one_literals = []

                # make linearity etc. constraints associated to d_r(source) = target
                # and for fixed r, assert d_r(source) has exactly one value (including zero, Undef)
                for target in target_classes:
                    diff = Differential(source, target, r)
                    diff_id = self.literal_manager.get_differential_id(diff)
                    if diff_id is None:
                        raise ValueError(
                            f"Differential {diff} not found in literal manager."
                        )
                    equals_one_literals.append(diff_id)
                    new_clauses = self.create_linearity_and_square0_clauses(diff)
                    if new_clauses != None:
                        all_clauses.append(new_clauses)
                card_constraint = CardEnc.equals(
                    lits=equals_one_literals, bound=1, encoding=9
                )
                cardinality_constraints.append(card_constraint)

                # if d_r(x) != 0 then d_{r+i}(x) = Undef for i > 0
                zero_diff = Differential(source, ZeroClass, r)
                zero_diff_atom = self.literal_manager.get_differential_atom(zero_diff)
                not_zero_clause = Neg(zero_diff_atom)
                higher_undef_atoms = []
                higher_r_list = [r1 for r1 in self.E1_page.r_with_nonzero_target(source.get_degree())
                                 if r1 > r]
                for higher_r in higher_r_list:
                    higher_diff = Differential(source, Undefined, higher_r)
                    higher_diff_atom = self.literal_manager.get_differential_atom(
                        higher_diff
                    )
                    higher_undef_atoms.append(higher_diff_atom)
                if higher_undef_atoms:
                    implies_clause = Implies(not_zero_clause, And(*higher_undef_atoms))
                    all_clauses.append(implies_clause)

                #this is to ensure that if a class is a cycle on the previous page, then differential on the r-th page is not undefined.
                #also d_r is not undefined for the first r with possible target
                undefined_diff = Differential(source, Undefined, r)
                undefined_atom = self.literal_manager.get_differential_atom(undefined_diff)

                r_lower_list = [rl for rl in self.E1_page.r_with_nonzero_target(source.get_degree())
                                if rl < r]
                if r_lower_list == []:
                    all_clauses.append(Neg(undefined_atom))
                else:
                    rl = max(r_lower_list)
                    lower_zero_diff = Differential(source, ZeroClass, rl)
                    lower_zero_atom = self.literal_manager.get_differential_atom(lower_zero_diff)

                    defined_clause = Implies(lower_zero_atom, Neg(undefined_atom))
                    all_clauses.append(defined_clause)


        # Want to say that every class participates in exactly one differential.
        # But it's possible for d_r(a) = c, d_r(b) = 0 => d_r(a+b) = c.
        # So we impose here every class is involved in *at least* one differential, and the
        # other direction is taken care of by the "square zero" constraints.
        for cls in self.E1_page.get_classes():

            hit_or_support_literals = []
#            print("tracing", cls)

            for r in self.E1_page.r_with_nonzero_source(cls.get_degree()):
                possible_sources = self.E1_page.get_possible_nontrivial_differential_sources(
                    cls, r
                )
#                print("possible sources", r, possible_sources)

                for source in possible_sources:
                    diff = Differential(source, cls, r)
                    diff_id = self.literal_manager.get_differential_id(diff)

                    if diff_id is None:
                        raise ValueError(
                            f"Differential {diff} not found in literal manager."
                        )

                    hit_or_support_literals.append(diff_id)

            for r in self.E1_page.r_with_nonzero_target(cls.get_degree()):
                possible_targets = self.E1_page.get_possible_differential_targets(
                    cls, r
                )
#                print("possible targets", r,  possible_targets)

                for target in possible_targets:
                    diff = Differential(cls, target, r)
                    diff_id = self.literal_manager.get_differential_id(diff)

                    if diff_id is None:
                        raise ValueError(
                            f"Differential {diff} not found in literal manager."
                        )

                    hit_or_support_literals.append(diff_id)


            card_constraint = CardEnc.atleast(
                lits=hit_or_support_literals, bound=1, encoding=9
            )
            cardinality_constraints.append(card_constraint)



        constraint = And(*all_clauses).simplified()
        print("len(variables) = ", len(self.literal_manager.differentials))
        print("len(all_clauses) = ", len(all_clauses))
        print("len(cardinality_constraints) = ", len(cardinality_constraints))
        print("len(known_clauses) = ", len(known_clauses))
        with Solver("Gluecard4") as s:
            for card in cardinality_constraints:
                s.append_formula(card)
            s.append_formula(constraint)
            s.solve(assumptions=known_clauses)
            all_models = []
            for model in s.enum_models(assumptions=known_clauses):
                formula_models = Formula.formulas(model, atoms_only=True)
                only_true = [
                    atom.object for atom in formula_models if not isinstance(atom, Neg)
                ]
                all_models.append(only_true)
            return all_models
