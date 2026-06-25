"""
This module defines the ExtClass class, which provides a 
useful abstraction for working with classes in the 
cohomology of the C-motivic steenrod algebra.
It also defines ZeroClass,
which is an instance of ExtClass that represents the zero class.
Finally there is Undefined which is the ``None" variant of ExtClass,
used as the ``target" of a differential when the source is not a cycle on the E_r page.
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
        if other == Undefined:
            return False

        return self.get_degree() == other.get_degree()

ZeroClass: ExtClass = None
Undefined: ExtClass = None
