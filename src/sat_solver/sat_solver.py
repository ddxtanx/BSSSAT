from sat_solver.ext_class import ZeroClass, Undefined, ExtClass
from sat_solver.differential import Differential
from sat_solver.ext import Ext
from sat_solver.literal_manager import LiteralManager
from sat_solver.hitbefore import HitBefore
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
                f"Creating literals with source {ext_class.get_classdegree()}, {ext_class.get_vector()}"
            )
            for r in self.E1_page.r_with_nonzero_target(ext_class.get_classdegree()):
                target_classes = [ZeroClass, Undefined]
                target_classes += self.E1_page.get_possible_differential_targets(
                    ext_class, r
                )
                for target_class in target_classes:
                    #print(
                    #    f"Creating differential literal: ({ext_class.tridegree}, {ext_class.vector})--d{r}--> ({target_class.tridegree}, {target_class.vector})"
                    #)
                    differential = Differential(ext_class, target_class, r)
                    self.literal_manager.add_differential_literal(differential)
        for r in range(1, self.max_differential + 1):
            #print(f"Creating differential literal: (None, [True])--d{r}--> (None, [True])")
            self.literal_manager.add_differential_literal(Differential(ZeroClass, ZeroClass, r))


    def create_hitbefore_clauses(self) -> list[list[int]]:
        """
        Creates the variables HitBefore(x, r) and the clauses defining them.
        If r_1 < ... < r_k are the lengths of the differentials that can hit x, then
        HitBefore(x, r_{i+1}) <=> HitBefore(x, r_i) or d_{r_i}(z) = x for some z.
        HitBefore(x, r_1) is always false, so it gets no variable, and
        HitBefore(x, r_k + 1) means that x is hit at all.
        """
        clauses = []
        for cls in self.E1_page.get_classes():
            pages = sorted(self.E1_page.r_with_nonzero_source(cls.get_classdegree()))
            if not pages:
                continue
            prev_hitbefore_id = None
            for r, next_r in zip(pages, pages[1:] + [pages[-1] + 1]):
                next_hitbefore_id = self.literal_manager.add_hitbefore_literal(HitBefore(cls, next_r)).name
                hit_ids = [
                    self.literal_manager.get_differential_id(Differential(source, cls, r))
                    for source in self.E1_page.get_possible_nontrivial_differential_sources(cls, r)
                ]
                for hit_id in hit_ids:
                    clauses.append([-hit_id, next_hitbefore_id])
                if prev_hitbefore_id is not None:
                    clauses.append([-prev_hitbefore_id, next_hitbefore_id])
                    hit_ids.append(prev_hitbefore_id)
                clauses.append([-next_hitbefore_id] + hit_ids)
                prev_hitbefore_id = next_hitbefore_id
        return clauses


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

        # d_r(0) = 0 always true
        for r in range(1, self.max_differential + 1):
            zero_differential = Differential(ZeroClass, ZeroClass, r)
            zero_atom = self.literal_manager.get_differential_atom(zero_differential)
            if zero_atom is not None:
                knowns.append(zero_atom)
            else:
                raise ValueError(
                    f"Zero differential {zero_differential} not found in literal manager."
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
#        source_degree = source.get_classdegree()
#        degree = diff.get_degree()
#        target = diff.get_target()

#        for other_class in self.E1_page.get_classes():
#            other_deg = other_class.get_classdegree()
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
        source_degree = source.get_classdegree()
        degree = diff.get_degree()
        target = diff.get_target()
        if target == Undefined:
            return None

# FIXME: this double-counts pairs of differentials to add
#for example, if we have three differentials d_r(x) = y, d_r(z) = w, and d_r(x + z) = y + w, then we will add the linearity clause for both (d_r(x), d_r(z)) and (d_r(z), d_r(x)), which is redundant. We should fix this to only add one of these clauses.
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
            for r1 in self.E1_page.r_with_nonzero_target(target.get_classdegree()):
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

        if len(conditional_consequents) > 0:
            consequent = And(*conditional_consequents)
            return Implies(antecedent, consequent)
        else:
            return None


#why do we have the following constriants in the sat solver? why not put them outside?
    def build_solver(self) -> tuple[Solver, list[int]]:
        """
        This method constructs literals and constraints for the SAT solver based on the E1 page, known differentials, and the Leibniz, linearity, and square-zero rules.
        Returns the solver and the assumptions encoding the known differentials.
        """
        self.create_literals()
        known_clauses = self.create_known_differential_clauses()
        all_clauses = []
        cardinality_constraints = []
        cardinality_constraints.append(self.create_hitbefore_clauses())
        for source in self.E1_page.get_classes():
            for r in self.E1_page.r_with_nonzero_target(source.get_classdegree()):
                target_classes = [ZeroClass, Undefined]
                target_classes += self.E1_page.get_possible_differential_targets(
                    source, r
                )
                equals_one_literals = []
                undef = Differential(source, Undefined, r)
                undef_id = self.literal_manager.get_differential_id(undef)

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
                # a source has to have at least one target, and undefined is incompatible with anything else
                card_constraint = CardEnc.atleast(
                    lits=equals_one_literals, bound=1, encoding=9
                )
                cardinality_constraints.append(card_constraint)
                for diff_id in equals_one_literals:
                    if diff_id != undef_id:
                        cardinality_constraints.append([[-undef_id, -diff_id]])

                # the true values of d_r(source) form one coset of the classes hit before page r
                values = [target for target in target_classes if target != Undefined]
                for y in values:
                    y_id = self.literal_manager.get_differential_id(Differential(source, y, r))
                    for y2 in values:
                        if y2 == y:
                            continue
                        y2_id = self.literal_manager.get_differential_id(Differential(source, y2, r))
                        hitbefore_id = self.literal_manager.get_hitbefore_id(HitBefore(y + y2, r))
                        if hitbefore_id is None:
                            cardinality_constraints.append([[-y_id, -y2_id]])
                        else:
                            cardinality_constraints.append(
                                [[-y_id, -y2_id, hitbefore_id], [-y_id, -hitbefore_id, y2_id]]
                            )

                # NEW CLAUSE: if a class is a source only for one differential.
                # if d_r(x) != 0 then d_{r+i}(x) = Undef for i > 0
                zero_diff = Differential(source, ZeroClass, r)
                zero_diff_atom = self.literal_manager.get_differential_atom(zero_diff)
                not_zero_clause = Neg(zero_diff_atom)
                higher_undef_atoms = []
                higher_r_list = [r1 for r1 in self.E1_page.r_with_nonzero_target(source.get_classdegree())
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

                r_lower_list = [rl for rl in self.E1_page.r_with_nonzero_target(source.get_classdegree())
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

#Question: How is this different then the previous cardinality constraints? The previous ones are for each source class and each r, while this is for each class overall. So this is a more global constraint, while the previous ones are more local constraints. This is to ensure that every class participates in at least one differential, while the previous ones are to ensure that each source class has exactly one target for each r.

        for cls in self.E1_page.get_classes():
            hit_or_support_literals = []
            pages = self.E1_page.r_with_nonzero_source(cls.get_classdegree())
            if pages:
                hit_or_support_literals.append(
                    self.literal_manager.get_hitbefore_id(HitBefore(cls, max(pages) + 1))
                )
            for r in self.E1_page.r_with_nonzero_target(cls.get_classdegree()):
                zero_id = self.literal_manager.get_differential_id(Differential(cls, ZeroClass, r))
                hit_or_support_literals.append(-zero_id)
            cardinality_constraints.append([hit_or_support_literals])



        constraint = And(*all_clauses).simplified()
        print("len(variables) = ", len(self.literal_manager.variables))
        print("len(all_clauses) = ", len(all_clauses))
        print("len(cardinality_constraints) = ", len(cardinality_constraints))
        print("len(known_clauses) = ", len(known_clauses))
        s = Solver("Gluecard4")
        for card in cardinality_constraints:
            s.append_formula(card)
        s.append_formula(constraint)
        return s, known_clauses

    def run_sat_solver(self) -> list[list[Differential]]:
        """
        Enumerates all models. Each model is the list of differentials that are true in it.
        """
        s, known_clauses = self.build_solver()
        with s:
            all_models = []
            for model in s.enum_models(assumptions=known_clauses):
                formula_models = Formula.formulas(model, atoms_only=True)
                only_true = [
                    atom.object for atom in formula_models if not isinstance(atom, Neg)
                                                              and isinstance(atom.object, Differential)
                ]
                all_models.append(only_true)
            return all_models

    def find_backbone(self) -> set[int]:
        """
        Returns the differential literals with the same value in every model:
        +id if that d_r(x) = y is true in every model, -id if it is false in every model.
        Starts from one model, then tests each remaining candidate by asking for a model where it fails;
        any model found that way also rules out every other candidate that fails in it.

        Raises:
            ValueError: If there is no model.
        """
        s, known_clauses = self.build_solver()
        with s:
            if not s.solve(assumptions=known_clauses):
                raise ValueError("No spectral sequence satisfies the constraints.")
            candidates = {
                lit for lit in s.get_model()
                if isinstance(self.literal_manager.get_differential_by_id(lit), Differential)
            }
            backbone = set()
            while candidates:
                lit = candidates.pop()
                if s.solve(assumptions=known_clauses + [-lit]):
                    candidates &= set(s.get_model())
                else:
                    backbone.add(lit)
            return backbone

    def find_forced_differentials(self, backbone: set[int]) -> list[Differential]:
        """
        Returns the differentials d_r(x) = y that are true in every model.
        """
        return [self.literal_manager.get_differential_by_id(lit) for lit in backbone if lit > 0]

    def find_unknown_differentials(self, backbone: set[int]) -> list[tuple[ExtClass, int]]:
        """
        Returns the pairs (x, r) for which the value of d_r(x) is not the same in every model.
        """
        unknown = []
        for source in self.E1_page.get_classes():
            for r in self.E1_page.r_with_nonzero_target(source.get_classdegree()):
                values = [ZeroClass, Undefined] + self.E1_page.get_possible_differential_targets(source, r)
                ids = [self.literal_manager.get_differential_id(Differential(source, y, r)) for y in values]
                if any(i not in backbone and -i not in backbone for i in ids):
                    unknown.append((source, r))
        return unknown
