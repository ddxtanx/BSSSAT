from .ext_class import ExtClass

UNDEFINED = -1
class Differential:
     def __init__(self, source: ExtClass, target: ExtClass) -> None:
        self.source = source
        self.target = target
        difference = (target.get_degree()[0] - source.get_degree()[0],
                      target.get_degree()[1] - source.get_degree()[1],
                      target.get_degree()[2] - source.get_degree()[2])
        if difference[1] != 1 or difference[2] < 1 or difference[2]-difference[0] != 1:
            raise ValueError("Invalid differential: target degree must be source degree + (r-1, 1, r) for some r >= 1")
        self.degree_of_differential = difference[2]

    def get_source(self) -> ExtClass:
        return self.source

    def get_target(self) -> ExtClass:
        """
        Returns the target of the differential as an ExtClass instance.
        """
        if self.degree_of_differential < 1:
            raise ValueError("degree_of_differential must be at least 1")
        target_degree = find_differential.add_degree(self.source.get_degree(), (self.degree_of_differential - 1, 1, self.degree_of_differential))
        basis = find_differential.class_index(target_degree)
        dimension = len(basis)

        # No classes in target degree: only zero is possible.
        if dimension == 0:
            return ExtClass(target_degree, [])

        # For now, we return Undefined to indicate that the target is not yet determined.
        return Undefined
    

    def is_cycle(self) -> bool:
        pass

    def get_tridegree(self) -> tuple[int, int, int]:
        pass

    def __hash__(self) -> int:
        pass

    def __eq__(self, other: object) -> bool:
        pass
"""
This module defined the Differential class which provides a 
useful interface for working with questions about the values of differentials.
"""

try:
    from .ext_class import ExtClass, ZeroClass, Undefined
except ImportError:
    from ext_class import ExtClass, ZeroClass, Undefined

class Differential:
    """
    This class represents a differential in the rho-Bockstein spectral sequence.
    """

    def __init__(self, source: ExtClass, r: int, target: ExtClass) -> None:
        self.source = source
        self.r = r
        self.target = target

    def get_source(self) -> ExtClass:
        """
        Returns the source of the differential as an ExtClass instance.
        """
        return self.source

    def get_target(self) -> ExtClass:
        """
        Returns the target of the differential as an ExtClass instance.
        """
        return self.target

    def is_cycle(self) -> bool:
        """
        Returns if the source of the differential is a cycle, i.e. if the target is ZeroClass.
        """
        return self.get_target() is ZeroClass

    def __hash__(self) -> int:
        return hash((self.get_source(), self.get_target()))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Differential):
            return False
        return self.get_source() == other.get_source() and self.get_target() == other.get_target()




if __name__ == "__main__":
    source = ExtClass((110, 34, 54), [1, 0, 0])
    print("The differentials for " + source.get_name() + ":")
    for r in range(1, 6):

        possible_targets = source.get_differential_targets(r)
        if not possible_targets:        #is this correct way to handle no targets? i don't wanna use zero class because as zero class is different from undefined, and we want to know if there are no targets, not if the target is zero class.
            continue

        print(f"d_{r} targets:")
        for target in possible_targets:
            print(" ", target.get_name())



