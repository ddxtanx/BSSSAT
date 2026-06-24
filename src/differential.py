"""
This module defined the Differential class which provides a 
useful interface for working with questions about the values of differentials.
"""

from .ext_class import ExtClass, ZeroClass, Undefined

class Differential:
    """
    This class represents a differential in the rho-Bockstein spectral sequence.
    """
    def get_source(self) -> ExtClass:
        """
        Returns the source of the differential as an ExtClass instance.
        """
        pass

    def get_target(self) -> ExtClass:
        """
        Returns the target of the differential as an ExtClass instance.
        """
        pass

    def is_cycle(self) -> bool:
        """
        Returns if the source of the differential is a cycle, i.e. if the target is ZeroClass.
        """
        return self.get_target() == ZeroClass 

    def __hash__(self) -> int:
        return hash((self.get_source(), self.get_target()))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Differential):
            return False
        return self.get_source() == other.get_source() and self.get_target() == other.get_target()
