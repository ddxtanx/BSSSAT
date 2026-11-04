"""
This class keeps track of the helper variables HitBefore(x, r) which says
whether x is the target of a d_i differential for i < r.
"""

from sat_solver.ext_class import Undefined
from sat_solver.ext_class import ExtClass, ZeroClass


class HitBefore:
    """
    This class represents an auxiliary variable in the solve that keeps track
    of whether a class x is the target of a differential of strictly smaller
    length than r.
    """

    def __init__(self, cls: ExtClass, r: int) -> None:
        self.cls = cls
        self.r = r

    def get_cls(self) -> ExtClass:
        """
        Returns the source of the differential as an ExtClass instance.
        """
        return self.cls

    def get_r(self) -> int:
        """
        Returns the degree of the differential as an integer.
        """
        return self.r

    def __hash__(self) -> int:
        return hash((self.get_cls(), self.get_r()))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, HitBefore):
            return False
        return (
            self.get_cls() == other.get_cls()
            and self.get_r() == other.get_r()
        )

    def __repr__(self) -> str:
        return f"HitBefore(class={self.cls}, r={self.r})"

    def __str__(self) -> str:
        return self.__repr__()
