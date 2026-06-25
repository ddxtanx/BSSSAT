from .ext_class import ZeroClass, Undefined, ExtClass
from .differential import Differential
from .ext import Ext
from .literal_manager import LiteralManager
from pysat.solvers import Solver
from pysat.formula import And, Implies, Neg, Formula
from pysat.card import CardEnc


class SATSolver:
    E1_page: Ext
    literal_manager: LiteralManager
    max_coweight: int
    max_differential: int
    known_differentials: dict[tuple[ExtClass, int], ExtClass]

    def __init__(self, E1_page: Ext, max_coweight: int, max_differential: int):
        self.E1_page = E1_page
        self.literal_manager = LiteralManager()
        if max_coweight < 0:
            raise ValueError("max_coweight must be non-negative")
        self.max_coweight = max_coweight
        self.max_differential = max_differential
        known_diffs = self.E1_page.get_known_differentials()
        for differential in known_diffs:
            source = differential.get_source()
            degree = differential.get_degree()
            target = differential.get_target()
            self.known_differentials[(source, degree)] = target

    def create_literals(self):
        classes = self.E1_page.get_classes_up_to_coweight(self.max_coweight)
        classes += [
            ZeroClass,
            Undefined,
        ]  # TODO: Verify that these are not already included in the list of classes
        for ext_class in classes:
            for r in range(1, self.max_differential + 1):
                target_classes = [ZeroClass, Undefined]
                target_classes += ext_class.get_differential_targets(r)
                for target_class in target_classes:
                    # TODO: Verify this is the interface Pengkun wants for creating a differential
                    differential = Differential(ext_class, target_class, r)
                    self.literal_manager.add_differential(differential)

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
            differential = Differential(source, target, degree)
            atom = self.literal_manager.get_differential_id(differential)
            if atom is not None:
                knowns.append(atom)
            else:
                raise ValueError(
                    f"Known differential {differential} not found in literal manager."
                )
        for r in range(1, self.max_differential + 1):
            zero_differential = Differential(ZeroClass, ZeroClass, r)
            zero_atom = self.literal_manager.get_differential_id(zero_differential)
            if zero_atom is not None:
                knowns.append(zero_atom)
            else:
                raise ValueError(
                    f"Zero differential {zero_differential} not found in literal manager."
                )

            undefined_differential = Differential(Undefined, Undefined, r)
            undefined_atom = self.literal_manager.get_differential_id(
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

    def create_clauses_from_assumed_differential(self, diff: Differential) -> Formula:
        """
        Given a differential question, this creates the clauses that enforce the Leibniz, linearity, and square-zero rules for this differential
        via implications.

        Args:
            diff (Differential): The differential question.

        Returns:
            Formula: A formula representing the implications of the Leibniz, linearity, and square-zero rules for the differential.

        Raises:
            ValueError: If the differential is not found in the literal manager.
            Errors raised by the Leibniz, linearity, or square-zero clause creation methods.
        """
        antecedent = self.literal_manager.get_differential_atom(diff)
        conditional_consequents = []

        source = diff.get_source()
        source_degree = source.get_degree()
        degree = diff.get_degree()
        target = diff.get_target()

        for other_class in self.E1_page.get_classes_up_to_coweight(self.max_coweight):
            other_deg = other_class.get_degree()
            if other_deg < source_degree:
                continue
            target_classes = [ZeroClass]
            target_classes += other_class.get_differential_targets(degree)
            for target_class in target_classes:
                other_diff = Differential(other_class, target_class, degree)
                other_antecedent = self.literal_manager.get_differential_atom(
                    other_diff
                )
                other_consequents = []

                leibniz_diff = self.create_leibniz_differentials(diff, other_diff)
                diff_source = leibniz_diff.get_source()
                diff_target = leibniz_diff.get_target()
                if (
                    diff_source.get_coweight() <= self.max_coweight
                    and diff_target.get_coweight() <= self.max_coweight
                ):
                    leibniz_consequent = self.literal_manager.get_differential_atom(
                        leibniz_diff
                    )
                    if leibniz_consequent is not None:
                        other_consequents.append(leibniz_consequent)
                    else:
                        raise ValueError(
                            f"Leibniz differential {leibniz_diff} not found in literal manager."
                        )

                if source.in_same_tridegree_as(other_class) and source != other_class:
                    linearity_diff = self.create_linearity_differential(
                        diff, other_diff
                    )
                    linearity_consequent = self.literal_manager.get_differential_atom(
                        linearity_diff
                    )
                    if linearity_consequent is not None:
                        other_consequents.append(linearity_consequent)
                    else:
                        raise ValueError(
                            f"Linearity differential {linearity_diff} not found in literal manager."
                        )

                other_consequent = And(*other_consequents)
                conditional_consequents.append(
                    Implies(other_antecedent, other_consequent)
                )

        square_zero_diff = Differential(target, ZeroClass, degree)
        square_zero_consequent = self.literal_manager.get_differential_atom(
            square_zero_diff
        )
        if square_zero_consequent is not None:
            conditional_consequents.append(square_zero_consequent)
        else:
            raise ValueError(
                f"Square-zero differential {square_zero_diff} not found in literal manager."
            )

        consequent = And(*conditional_consequents)
        return Implies(antecedent, consequent)

    def run_sat_solver(self):
        """
        This method constructs literals and constraints for the SAT solver based on the E1 page, known differentials, and the Leibniz, linearity, and square-zero rules.
        Satisfiability is tested and models are enumerated.
        """
        self.create_literals()
        known_clauses = self.create_known_differential_clauses()
        all_clauses = []
        cardinality_constraints = []
        for source in self.E1_page.get_classes_up_to_coweight(self.max_coweight):
            for r in range(1, self.max_differential + 1):
                equals_one_literals = []
                target_classes = [ZeroClass, Undefined]
                target_classes += source.get_differential_targets(r)
                for target in target_classes:
                    diff = Differential(source, target, r)
                    diff_id = self.literal_manager.get_differential_id(diff)
                    if diff_id is None:
                        raise ValueError(
                            f"Differential {diff} not found in literal manager."
                        )
                    equals_one_literals.append(diff_id)
                    all_clauses.append(
                        self.create_clauses_from_assumed_differential(diff)
                    )
                card_constraint = CardEnc.equals(
                    lits=equals_one_literals, bound=1, encoding=9
                )
                cardinality_constraints.append(card_constraint)

                zero_diff = Differential(source, ZeroClass, r)
                zero_diff_atom = self.literal_manager.get_differential_atom(zero_diff)
                not_zero_clause = Neg(zero_diff_atom)
                higher_undef_atoms = []
                for higher_r in range(r + 1, self.max_differential + 1):
                    higher_diff = Differential(source, Undefined, higher_r)
                    higher_diff_atom = self.literal_manager.get_differential_atom(
                        higher_diff
                    )
                    higher_undef_atoms.append(higher_diff_atom)
                if higher_undef_atoms:
                    implies_clause = Implies(not_zero_clause, And(*higher_undef_atoms))
                    all_clauses.append(implies_clause)

        constraint = And(*all_clauses).simplified()
        with Solver("Gluecard4") as s:
            for card in cardinality_constraints:
                s.append_formula(card)
            s.append_formula(constraint)
            s.solve(assumptions=known_clauses)
            for model in s.enum_models():
                formula_models = Formula.formulas(model, atoms_only=True)
                only_true = [
                    atom for atom in formula_models if not isinstance(atom, Neg)
                ]
                print(f"Model: {only_true}")
