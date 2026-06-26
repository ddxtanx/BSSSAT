"""
This module defines the ExtClass class, which provides a
useful abstraction for working with classes in the
cohomology of the C-motivic steenrod algebra.
It also defines ZeroClass,
which is an instance of ExtClass that represents the zero class.
Finally there is Undefined which is the ``None" variant of ExtClass,
used as the ``target" of a differential when the source is not a cycle on the E_r page.
"""

from tkinter.font import names
from itertools import product

try:
    from . import Main_code_for_diffls

except ImportError:
    import Main_code_for_diffls


class ExtClass:
    """
    This class represents a class in the cohomology of the C-motivic steenrod algebra.
    """
    def __init__(self, tridegree: tuple[int, int, int], vector: list[bool]) -> None:
        self.tridegree = tridegree
        self.vector = vector


    def get_name(self) -> str:
        """
         Returns the name of the class as a string.
        """
        classes = Main_code_for_diffls.class_index(self.tridegree)
        names = []
        for index, coefficient in enumerate(self.vector):
            if coefficient:
                names.append(classes[index]["name"])
        if not names:
            return "0"
        return " + ".join(names)

    def get_degree(self) -> tuple[int, int, int]:
        """
        Returns the tridegree (s, f, w) of the class as a tuple of three integers.
        """
        return (self.tridegree)

    def get_differential_targets(self, r: int) -> list[ExtClass]:
        """
        Returns all possible targets y for a differential d_r(x) = rho^r y.

        This includes every linear combination in the target tridegree, and the
        zero target (all coefficients False).
        """
        if r < 1:
            raise ValueError("r must be at least 1")

        source_degree = self.get_degree()
        target_degree = Main_code_for_diffls.add_degree(source_degree, (r - 1, 1, r))
        basis = Main_code_for_diffls.class_index(target_degree)
        dimension = len(basis)

        # No classes in target degree: only zero is possible.
        if dimension == 0:
            return [ExtClass(target_degree, [])]

        targets: list[ExtClass] = []
        for coeffs in product([False, True], repeat=dimension):
            targets.append(ExtClass(target_degree, list(coeffs)))
        return targets

    def __add__(self, other: ExtClass) -> ExtClass:
        """
        Constructs a new ExtClass instance that represents the sum of this class and another class.

        Args:
            other (ExtClass): The other ExtClass instance to add to this class.
        Args:
            other (ExtClass): The other ExtClass instance to add to this class.

        Returns:
            ExtClass: A new ExtClass instance that represents the sum of this class and the other
        """
        if self.get_degree() != other.get_degree():
            raise ValueError("Can only add Ext classes in the same tridegree")
        if len(self.vector) != len(other.vector):
            raise ValueError("Can only add Ext classes with the same vector length")
        else :
            new_vector = [a ^ b for a, b in zip(self.vector, other.vector)]
            return ExtClass(self.get_degree(), new_vector)

    def __mul__(self, other: ExtClass) -> ExtClass:
#         """
#         Constructs a new ExtClass instance that represents the product of this class and another class.
#         This either just returns the naive juxtaposition of the two classes,
#         or it returns the result of a known product in the Ext algebra.

#         Args:
#             other (ExtClass): The other ExtClass instance to multiply with this class.

#         Returns:
#             ExtClass: A new ExtClass instance that represents the product of this class and the other
#         """
        pass  # Placeholder for the actual implementation of the product operation.

    def get_tau_torsion(self) -> int:



    def get_name_latex(self) -> str:
        """
        Returns the name of the class in LaTeX format as a string.
        """
        return Main_code_for_diffls.convert_to_latex(self.get_name())

    def __hash__(self) -> int:
        return hash((self.tridegree, tuple(self.vector)))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ExtClass):
            return False
        return self.tridegree == other.tridegree and self.vector == other.vector


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
   
def zeroclass_at_degree(tridegree: tuple[int, int, int]) -> ExtClass:
    """
    Returns a new ExtClass instance that represents the zero class in a given tridegree.
    """
    target_element = Main_code_for_diffls.class_index(tridegree)
    dimension = len(target_element)
    if dimension == 0:
        return ExtClass(tridegree, [])
    else:
        return ExtClass(tridegree, [False] * dimension)





Undefined: ExtClass = None
#         Returns:
#             bool: True if this class and other are in the same tridegree, False otherwise
#         """



#test
if __name__ == "__main__":
    x = ExtClass((0, 0, -1), [1, 0, 0])
    x = ExtClass((0, 0, -1), [1, 0, 0])
    print(x.get_name())

    for target in x.get_differential_targets(2):
        print(target.get_name())

    y = ExtClass((110, 34, 54), [1, 0, 0])
    z = ExtClass((110, 34, 54), [0, 1, 0])
    t = ExtClass((110, 34, 54), [1, 0, 0])

    print((t + y).get_name())
    print((t + z).get_name())

    m = ExtClass((110, 27, 58), [1, 1, 0])
    print(m.get_name())
    print(m.get_name_latex())

    print(x.in_same_tridegree_as(y))
    print(x.in_same_tridegree_as(z))
    print(x.in_same_tridegree_as(ZeroClass))
    

