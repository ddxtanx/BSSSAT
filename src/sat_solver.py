from pysat.formula import Formula
from .ext_class import ZeroClass, Undefined, ExtClass
from .differential import Differential
from .ext import Ext
from .literal_manager import LiteralManager
from pysat.solvers import Solver
from pysat.formula import And, Or, Implies

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
        classes += [ZeroClass, Undefined] #TODO: Verify that these are not already included in the list of classes
        for ext_class in classes:
            for r in range(1, self.max_differential + 1):
                target_classes = [ZeroClass, Undefined]
                target_classes += ext_class.get_differential_targets(r)
                for target_class in target_classes:
                    #TODO: Verify this is the interface Pengkun wants for creating a differential
                    differential = Differential(ext_class, target_class, r)
                    self.literal_manager.add_differential(differential)

    def create_known_differential_clauses(self) -> Formula:
        """
        This creates the composite clause that enforces the known differentials in the SAT solver.

        Returns:
            Formula: A formula representing the known differentials. Really just an AND of all the differential questions known to be True.

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
                raise ValueError(f"Known differential {differential} not found in literal manager.")
        for r in range(1, self.max_differential + 1):
            zero_differential = Differential(ZeroClass, ZeroClass, r)
            zero_atom = self.literal_manager.get_differential_id(zero_differential)
            if zero_atom is not None:
                knowns.append(zero_atom)
            else:
                raise ValueError(f"Zero differential {zero_differential} not found in literal manager.")

            undefined_differential = Differential(Undefined, Undefined, r)
            undefined_atom = self.literal_manager.get_differential_id(undefined_differential)
            if undefined_atom is not None:
                knowns.append(undefined_atom)
            else:
                raise ValueError(f"Undefined differential {undefined_differential} not found in literal manager.")
        return And(*knowns)

    def create_at_most_one_clauses(self) -> list[list[int]]:
        """
        This creates the composite clause that enforces the "at most one" condition for each source class and differential degree.

        Returns:
            list[list[int]]: A list of clauses representing the "at most one" condition for each source class and differential degree.
        """
        clauses = []
        classes = self.E1_page.get_classes_up_to_coweight(self.max_coweight)
        classes += [ZeroClass, Undefined] #TODO: Verify that these are not already included in the list of classes
        for ext_class in classes:
            for r in range(1, self.max_differential + 1):
                target_classes = [ZeroClass, Undefined]
                target_classes += ext_class.get_differential_targets(r)
                differential_literals = []
                for target_class in target_classes:
                    differential = Differential(ext_class, target_class, r)
                    atom = self.literal_manager.get_differential_id(differential)
                    if atom is not None:
                        differential_literals.append(atom.name)
                    else:
                        raise ValueError(f"Differential {differential} not found in literal manager.")
                
                clauses.append(differential_literals)
                

                

