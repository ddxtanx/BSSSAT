"""
This module defines the ExtClass class, which provides a
useful abstraction for working with classes in the
cohomology of the C-motivic steenrod algebra.
It also defines ZeroClass,
which is an instance of ExtClass that represents the zero class.
Finally there is Undefined which is the ``None" variant of ExtClass,
used as the ``target" of a differential when the source is not a cycle on the E_r page.
"""
from __future__ import annotations
from itertools import product
from sat_solver.E1_csv_parser import E1CsvParser

class ExtClass:
    """
    
    This class represents a class in the cohomology of the C-motivic steenrod algebra.
    """

    def __init__(self, tridegree: tuple[int, int, int], vector: list[bool]) -> None:
        self.tridegree = tridegree
        self.vector = vector
#
    def get_classdegree(self) -> tuple[int, int, int]:
        """
        Returns the tridegree (s, f, w) of the class as a tuple of three integers.
        """
        return self.tridegree
#
    def get_vector(self) -> list[bool]:
        """
        Returns the F2 vector of the class as a list of booleans.
        """
        return self.vector

#
    def __add__(self, other: ExtClass) -> ExtClass:
        """
        adds two ExtClass 
        """
        if self == ZeroClass:
            return other
        if other == ZeroClass:
            return self
        if self.get_classdegree() != other.get_classdegree():
            raise ValueError("Can only add Ext classes in the same tridegree")
        if len(self.vector) != len(other.vector):
            raise ValueError("Can only add Ext classes with the same vector length")
        else:
            new_vector = [a ^ b for a, b in zip(self.vector, other.vector)]
            is_nonzero = any(new_vector)
            if not is_nonzero:
                return ZeroClass
            return ExtClass(self.get_classdegree(), new_vector)


    #we need to add a function to multiply two ExtClasses.
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


# Check if we need it, maybe in the end to print the real names.
    def class_name(self, E1: "E1CsvParser") -> str:
        """
        Returns the name of this ExtClass element based on its vector representation.
        """
        deg = self.get_classdegree()
        vector = self.get_vector()
        if deg == None:
            if vector == [True]:
                return "0"
            elif vector == [False]:
                return "Undef"
            else:
                raise ValueError(f"Invalid element (None, {vector})")
        basis = E1.sfw_dict.get(deg)
        if basis is None:
             raise ValueError(f"Degree {deg} not found in E1.sfw_dict")
        return " + ".join(b["name"] for b, on in zip(basis, vector) if on)




 # Check if we need it. I suspect it will be needed when writing multiplication function.
    @staticmethod
    def create_class_from_basis_name(E1:"E1CsvParser", degree, name) -> "ExtClass":
        basis = E1.sfw_dict.get(degree)
        if basis is None:
            raise ValueError(f"Degree {degree} not found in E1.sfw_dict")
        vector = [False] * len(basis)
        for i, element in enumerate(basis):
            if element["name"] == name:
                vector[i] = True
                return ExtClass(degree, vector)
        raise ValueError(
            f"{name!r} is not a basis element in degree {degree}"
        )


    def get_tau_torsion(self, E1: "E1CsvParser") -> int:
        """ Return the tau-torsion of this class. """
        if self == ZeroClass or self == Undefined:
            return 0
        basis = E1.sfw_dict.get(self.get_classdegree())
        if basis is None:
            raise ValueError(
                f"Degree {self.get_classdegree()} not found in E1.sfw_dict"
            )
        vector = self.get_vector()
        if len(vector) != len(basis):
            raise ValueError(
                f"Vector length {len(vector)} does not match dimension "
                f"{len(basis)} in degree {self.get_classdegree()}"
            )
        selected_torsions = [
            element["tautorsion"]
            for element, coefficient in zip(basis, vector)
            if coefficient
        ]
        if not selected_torsions:
            return 0
    #is it possible that x and y are both nonzero and torsion-free, but x+y is torsion? in our range!
        if 0 in selected_torsions:
            return 0
        return max(selected_torsions)


    # def get_name_latex(self) -> str:
    #     """
    #     Returns the name of the class in LaTeX format as a string.
    #     """
    #     return Main_code_for_diffls.convert_to_latex(self.get_name())

#check whether this function is used anywhere, if not delete it.
    def __hash__(self) -> int:
        return hash((self.tridegree, tuple(self.vector)))


#check whether this function is used anywhere, if not delete it.
    def __eq__(self, other: object) -> bool:
        """
        Determines whether this class and other are equal.
        """
        if not isinstance(other, ExtClass):
            return False
        return self.tridegree == other.tridegree and self.vector == other.vector

#check whether this function is used anywhere, if not delete it.
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

        return self.get_classdegree() == other.get_classdegree()


#
    def get_coweight(self) -> int:
        """
        Returns the coweight s - w of the class as an integer.
        """
        s, f, w = self.get_classdegree()
        return s - w

    def __repr__(self) -> str:
        """
        Returns a string representation of the ExtClass instance.
        """
        return f"ExtClass(tridegree={self.tridegree}, vector={self.vector})"

    def __str__(self) -> str:
        """
        uses the __repr__ method to return a string representation of the ExtClass instance.
        """
        return self.__repr__()

ZeroClass: ExtClass = ExtClass(None, [True])
Undefined: ExtClass = ExtClass(None, [False])

#we need to be careful about zero class and 0 in each degree. Should we make a function that treats 0 in each degree as a zero class? 



 