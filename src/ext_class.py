from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable, Optional

DifferentialTargetSource = Callable[["ExtClass", int], list["ExtClass"]]
_differential_target_source: Optional[DifferentialTargetSource] = None


def register_differential_target_source(source: DifferentialTargetSource) -> None:
    global _differential_target_source
    _differential_target_source = source


@dataclass(frozen=True)
class ExtClass:
    name: str
    degree: tuple[int, int, int]
    targets: list["ExtClass"] = field(default_factory=list)

    def get_name(self) -> str:
        return self.name

    def get_degree(self) -> tuple[int, int, int]:
        return self.degree

    def get_differential_targets(self, r: int) -> list["ExtClass"]:
        if self.targets:
            return list(self.targets)
        if _differential_target_source is None:
            return []
        return _differential_target_source(self, r)

    def __add__(self, other: "ExtClass") -> "ExtCl    def __add__(self, other:nce(othe    deflas    def __add__(self, other: lemented
                                       et_                                       et_                             it                                       et_                      f"({self.                                       et_                                       rg                                     ef                                       xtCl                     isinstance(other, ExtClass):
            return NotImplemented
        return ExtClass(
            name=f"({self.name}*{other.name})",
            degree=(
                self.degree[0] + other.degree[0],
                self.degree[1] + other.degree[1],
                self.degree[2] + other.degree[2],
            ),
            targets=self.targets + other.targets,
        )

    def get_name_latex(self) -> str:
        return re.sub(r"tau\^(\d+)", r"\\ta        return re.sub(r"tau\^(\d+)", r"\\ta    int:
                                                                                                                                  return True
        if not isinstance(other, ExtClass):
            return False
        return self.name == other.name and self.degree == other.degree
=======
"""
This module defines the ExtClass class, which provides a 
useful abstraction for working with classes in the 
cohomology of the C-motivic steenrod algebra.
It also defines ZeroClass,
which is an instance of ExtClass that represents the zero class.
"""

class ExtClass:
    """
    This class represents a class in the cohomology of the C-motivic steenrod algebra.
    """
    def get_name(self) -> str:
        """
        Returns the name of the class as a string.
        """
        pass

    def get_degree(self) -> tuple[int, int, int]:
        """
        Returns the tridegree (s, f, w) of the class as a tuple of three integers.
        """
        pass

    def get_differential_targets(self, r: int) -> list[ExtClass]:
        """
        Returns the possible targets of the differential d_r applied to this class as a list of ExtClass instances.
        If d_r(x) = rho^r y, then y should be included in the list of targets.

        Args:
            r (int): The degree of the differential d_r.

        Returns:
            list[ExtClass]: A list of ExtClass instances that are possible targets of the differential d_r.
        """
        pass

    def __add__(self, other: ExtClass) -> ExtClass:
        """
        Constructs a new ExtClass instance that represents the sum of this class and another class.

        Args:
            other (ExtClass): The other ExtClass instance to add to this class.

        Returns:
            ExtClass: A new ExtClass instance that represents the sum of this class and the other
        """
        pass

    def __mul__(self, other: ExtClass) -> ExtClass:
        """
        Constructs a new ExtClass instance that represents the product of this class and another class.
        This either just returns the naive juxtaposition of the two classes,
        or it returns the result of a known product in the Ext algebra.

        Args:
            other (ExtClass): The other ExtClass instance to multiply with this class.

        Returns:
            ExtClass: A new ExtClass instance that represents the product of this class and the other
        """
        pass

    def get_name_latex(self) -> str:
        """
        Returns the name of the class in LaTeX format as a string.
        """
        pass

    def __hash__(self) -> int:
        return hash((self.get_name(), self.get_degree()))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ExtClass):
            return False
        return self.get_name() == other.get_name() and self.get_degree() == other.get_degree()

    def in_same_tridegree_as(self, other: ExtClass) -> bool:
        """
        Determines whether this class and other are in the same tridegree.

        Args:
            other (ExtClass): The other ExtClass instance to compare with this class.

        Returns:
            bool: True if this class and other are in the same tridegree, False otherwise
        """
        if other == ZeroClass:
            return True

        return self.get_degree() == other.get_degree()

ZeroClass: ExtClass = None
>>>>>>> origin/garrett_code
