"""
This module provides a class for efficiently and correctly
managing the translation between questions about values of
differentials (i.e. "Is d_8(tau^(2^8)) = 0?") and the 
boolean literals expected by the SAT solver.
It is responsible for assigning to each differential question
an Atom representing the question, and for quickly returning 
the differential question associated to the given literal representation.
"""

from .differential import Differential
from pysat.formula import Atom, CNF

class LiteralManager:
    """
    A class to manage the translation between differential questions
    and boolean literals for a SAT solver.
    """

    differentials_to_ids: dict[Differential, Atom]
    differentials: list[Differential]

    def __init__(self):
        """
        Initializes the LiteralManager with empty lists and dictionaries.
        """
        self.differentials_to_ids = {}
        self.differentials = []

    def add_differential(self, differential: Differential) -> Atom:
        """
        Adds a new differential question to the manager and returns its unique ID.
        If the differential already exists, returns its existing ID.

        Args:
            differential (Differential): The differential question to add.
        Returns:
            int: The unique ID assigned to the differential question.
        Raises:
            ValueError: If the assigned ID does not match the expected value.
        """
        if differential in self.differentials_to_ids:
            return self.differentials_to_ids[differential]
        else:
            atom = Atom(differential)
            atom.clausify()
            self.differentials_to_ids[differential] = atom
            ident = atom.name
            if ident != len(self.differentials) + 1:
                raise ValueError(f"Unexpected literal ID {ident} for differential {differential}. Expected {len(self.differentials) + 1}.")
            self.differentials.append(differential)
            return atom

    def get_differential_id(self, differential: Differential) -> Atom | None:
        """
        Retrieves the Atom for a given differential question.

        Args:
            differential (Differential): The differential question to look up.
        Returns:
            Atom | None: The Atom representing the differential question, or None if it doesn't exist
        """
        return self.differentials_to_ids.get(differential, None)

    def get_differential_atom(self, differential: Differential) -> Atom | None:
        """
        Retrieves the Atom for a given differential question.

        Args:
            differential (Differential): The differential question to look up.

        Returns:
            Atom | None: The Atom representing the differential question, or None if it doesn't exist
        """
        return self.differentials_to_ids.get(differential, None)

    def get_differential_by_id(self, id: int) -> Differential | None:
        """
        Retrieves the differential question associated with a given ID.

        Args:
            id (int): The unique ID of the differential question. This also accepts the *negative* of the ID, which corresponds to the negation of the differential question.
                      This id is meant to be retreivied from the SAT solver's model, which returns a list of integers representing the literals that are true in the model.
        Returns:
            Differential | None: The differential question associated with the ID, or None if it doesn't exist
        """
        id = abs(id)
        if 1 <= id <= len(self.differentials):
            return self.differentials[id - 1]
        else:
            return None

