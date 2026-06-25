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
import re


import find_differential

class ExtClass:
    """
    This class represents a class in the cohomology of the C-motivic steenrod algebra.
    """
    def __init__(self, tridegree: tuple[int, int, int], vector: list[bool])-> None:
        self.tridegree = tridegree
        self.vector = vector


    def get_name(self) -> str:
        """
         Returns the name of the class as a string.
        """
        classes = find_differential.class_index(self.tridegree)
        names = []
        for index, coefficient in enumerate(self.vector):
            if coefficient:
                names.append(classes[index]["name"])
            else:
                None

        return " + ".join(names)

    def get_degree(self) -> tuple[int, int, int]:
        """
        Returns the tridegree (s, f, w) of the class as a tuple of three integers.
        """
        return (self.tridegree)

    def get_differential_targets(self, r: int) -> list["ExtClass"]:
        """
        Returns the possible targets of the differential d_r applied to this class as a list of ExtClass instances.
        If d_r(x) = rho^r y, then y should be included in the list of targets.
        """
        target_degree = find_differential.add_degree(self.get_degree(),(r - 1, 1, r))

        target_elements = find_differential.element_by_degree(target_degree)

        targets = []
        for index in range(len(target_elements)):
            vector = [0] * len(target_elements)
            vector[index] = 1
            targets.append(ExtClass(target_degree, vector))

        return targets
        

    def __add__(self, other: ExtClass) -> ExtClass:
        """
        Constructs a new ExtClass instance that represents the sum of this class and another class.

        Args:
            other (ExtClass): The other ExtClass instance to add to this class.

        Returns:
            ExtClass: A new ExtClass instance that represents the sum of this class and the other
        """
        if self.get_degree() != other.get_degree():
            raise ValueError("Cannot add ExtClass instances with different degrees")

        #if len(self.vector) != len(other.vector):
         #   raise ValueError("Cannot add ExtClass instances with different vector lengths")

        new_vector = []
        for a, b in zip(self.vector, other.vector):
            new_vector.append((a + b) % 2)

        return ExtClass(self.get_degree(), new_vector)

#     def __mul__(self, other: ExtClass) -> ExtClass:
#         """
#         Constructs a new ExtClass instance that represents the product of this class and another class.
#         This either just returns the naive juxtaposition of the two classes,
#         or it returns the result of a known product in the Ext algebra.

#         Args:
#             other (ExtClass): The other ExtClass instance to multiply with this class.

#         Returns:
#             ExtClass: A new ExtClass instance that represents the product of this class and the other
#         """
#         return ExtClass(
#             f"{self.name} {other.name}",
#             self.stem + other.stem,
#             self.adams_filtration + other.adams_filtration,
#             self.weight + other.weight,
#             min(self.tautorsion, other.tautorsion),
#             self._ext,
#         )


    def get_name_latex(self) -> str:
        """
        Returns the name of the class in LaTeX format as a string.
        """
        name = self.get_name()

        name = name.replace("tau", r"\tau")
        name = name.replace("rho", r"\rho")

        # Change exponents like ^4 into ^{4}
        name = re.sub(r"\^(\d+)", r"^{\1}", name)

        # Change names like h0, h1, d0, e0 into h_{0}, h_{1}, d_{0}, e_{0}
        name = re.sub(r"\b([a-zA-Z])(\d+)\b", r"\1_{\2}", name)

        return name


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
Undefined: ExtClass = None

if __name__ == "__main__":
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

