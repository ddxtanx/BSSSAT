"""
This module defined the Differential class which provides a
useful interface for working with questions about the values of differentials.
"""

from sat_solver.ext_class import Undefined
from sat_solver.ext_class import ExtClass, ZeroClass


class Differential:
    """
    This class represents a differential in the rho-Bockstein spectral sequence.
    """

    def __init__(self, source: ExtClass, target: ExtClass, degree: int) -> None:
        self.source = source
        self.target = target
        self.degree_of_differential = degree
        if (
            target != ZeroClass
            and target != Undefined
            and source != ZeroClass
            and source != Undefined
        ):
            difference = (
                target.get_degree()[0] - source.get_degree()[0],
                target.get_degree()[1] - source.get_degree()[1],
                target.get_degree()[2] - source.get_degree()[2],
            )
            if difference != (degree - 1, 1, degree):
                raise ValueError(
                    "Invalid differential: target degree must be source degree + (r-1, 1, r) for some r >= 1"
                )

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

    def get_degree(self) -> int:
        """
        Returns the degree of the differential as an integer.
        """
        return self.degree_of_differential

    def is_cycle(self) -> bool:
        """
        Returns if the source of the differential is a cycle, i.e. if the target is ZeroClass.
        """
        return self.get_target() == ZeroClass

    def __hash__(self) -> int:
        return hash((self.get_source(), self.get_target(), self.get_degree()))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Differential):
            return False
        return (
            self.get_source() == other.get_source()
            and self.get_target() == other.get_target()
            and self.get_degree() == other.get_degree()
        )

    def __repr__(self) -> str:
        return f"Differential(source={self.source}, target={self.target}, degree={self.degree_of_differential})"

    def __str__(self) -> str:
        return self.__repr__()


if __name__ == "__main__":
    source = ExtClass((110, 34, 54), [1, 0, 0])
    print("The differentials for " + source.get_name() + ":")
    for r in range(1, 6):
        possible_targets = source.get_differential_targets(r)
        if not possible_targets:  # is this correct way to handle no targets? i don't wanna use zero class because as zero class is different from undefined, and we want to know if there are no targets, not if the target is zero class.
            continue

        print(f"d_{r} targets:")
        for target in possible_targets:
            print(" ", target.get_name())
