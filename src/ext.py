"""
This module defines the Ext class which serves as the interface to 
interact with the entire cohomology of the C-motivic Steenrod Algebra
all at once. It provides methods to retrieve various kinds of elements
in the Ext algebra that should be useful for the creation of SAT constraints.
In addition, it should also provide methods to assert and to retrieve
known differentials that will be used to bootstrap the SAT solver.
"""

import csv

from .ext_class import ExtClass
from .differential import Differential
from .find_differential import get_classes()  
"""from some document import rho-periodic_list, which is a list of rho-periodic elements"""
"""from some document import product_dict, which stores [element1, element2, their product]"""


classes= get_classes()

class Ext:
    """
    This class represents useful pieces of information contained in the cohomology of the C-motivic Steenrod algebra.
    """
    def __init__(self, coweight, tridegree, classes, differentials):
        self.coweight = coweight
        self.tridegree = tridegree
        self.classes = classes['stem']
        self.differentials = differentials


    def get_classes_up_to_coweight(self, coweight: int) -> list[ExtClass]:
        """
        This method returns a list of ExtClasses whose coweight (s - w) is less that a given maximum,
        which we will attempt to resolve questions about differentials.

        Args:
            coweight (int): The maximum coweight s - w of the ExtClasses to retrieve.

        Returns:
            list[ExtClass]: A list of all the ExtClasses whose coweight is less than the given maximum.
        """ 
        classes_up_to_coweight = []
        for element in classes:
            if element['stem'] - element['weight'] <= coweight:
                classes_up_to_coweight.append(ExtClass(element['name'], (element['stem'], element['Adams filtration'], element['weight'])))
        return classes_up_to_coweight

    def get_classes_in_fixed_degree(self, N: int) -> list[ExtClass]:
        """
        This method returns a list of ExtClasses whose fixed degree (s + f - w) is equal to a given value N.

        Args:
            N (int): The fixed degree s + f - w of the ExtClasses to retrieve

        Returns:
            list[ExtClass]: A list of all the ExtClasses whose fixed degree is equal to N.
        """
        classes_with_N=[]
        for element in classes:
            if element['stem'] + element['Adams filtration'] - element['weight'] == N:
                classes_with_N.append(ExtClass(element['name'], (element['stem'], element['Adams filtration'], element['weight'])))
        return classes_with_N

    def get_classes_in_tridegree(self, tridegree: tuple[int, int, int]) -> list[ExtClass]:
        """
        This method returns a list of ExtClasses in a given tridegree (s, f, w).

        Args:
            tridegree (tuple[int, int, int]): The tridegree (s, f, w) of the ExtClasses to retrieve.

        Returns:
            list[ExtClass]: A list of all the ExtClasses in the given tridegree.
        """
        classes_in_tridegree = []
        for element in classes:
            if (element['stem'], element['Adams filtration'], element['weight']) == tridegree:
                classes_in_tridegree.append(ExtClass(element['name'], (element['stem'], element['Adams filtration'], element['weight'])))
        return classes_in_tridegree

    def get_rho_periodic_elements(self) -> list[ExtClass]:
        """
        This method returns a list of ExtClasses that are known to be permanent cycles from the E1 page,
        equivalently elements in the R-motivic Ext after inverting rho.
        Since these are known to be permanent cycles, we can enforce that their differentials are zero in the SAT solver
        which will help to bootstrap the solver and reduce the search space.

        Returns:
            list[ExtClass]: A list of all the ExtClasses that are known to be rho periodic.
        """
        classes_rho_periodic=[]
        for element in classes:
            if element['stem']+element['Adam filtration']-2*element['weight'] == 0:
                classes_rho_periodic.append(ExtClass(element['name'], (element['stem'], element['Adams filtration'], element['weight'])))
        return classes_rho_periodic

    def is_rho_periodic(self, ext_class: ExtClass) -> bool:
        """
        This method returns whether a given ExtClass is known to be rho periodic.

        Args:
            ext_class (ExtClass): The ExtClass to check for rho periodicity.

        Returns:
            bool: True if the ExtClass is known to be rho periodic, False otherwise.
        """
        if ext_class.degree[0] + ext_class.degree[1] - 2 * ext_class.degree[2] == 0:
            return True
        otherwise:
            return False

    def get_h1_periodic_elements(self) -> list[ExtClass]:
        """
        This method returns a list of ExtClasses that are h1 periodic (/torsion-free) element in the C-motivic Ext.
        Such elements complicate splitting via fixed degrees so we should detect them and have some separate method of handling them.

        Returns:
            list[ExtClass]: A list of all the ExtClasses that are known to be h1 periodic.
        """
        classes_h1_periodic=[]
        for element in classes:
            for rho_periodic_element in rho_periodic_list:
                if element.name == rho_periodic_element:
                    classes_h1_periodic.append(ExtClass(element['name'], (element['stem'], element['Adams filtration'], element['weight'])))
        return classes_h1_periodic

    def is_h1_periodic(self, ext_class: ExtClass) -> bool:
        """
        This method returns whether a given ExtClass is known to be h1 periodic.

        Args:
            ext_class (ExtClass): The ExtClass to check for h1 periodicity.

        Returns:
            bool: True if the ExtClass is known to be h1 periodic, False otherwise.
        """
        for rho_periodic_element in rho_periodic_list:
            if ext_class.name == rho_periodic_element:
                return True
        return False

    def get_known_differentials(self) -> list[Differential]:
        """
        This method returns a list of known differentials in the rho-Bockstein spectral sequence.

        Returns:
            list[Differential]: A list of all the known differentials in the rho-Bockstein spectral sequence.
        """
        return differentials

    def add_known_differential(self, differential: Differential) -> None:
        """
        This method adds a known differential to the list of known differentials in the rho-Bockstein spectral sequence.

        Args:
            differential (Differential): The Differential to add to the list of known differentials.
        """
        return self.differentials().append(differential)


