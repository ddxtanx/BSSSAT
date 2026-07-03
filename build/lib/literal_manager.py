"""
This module provides a class for efficiently and correctly
managing the translation between questions about values of
differentials (i.e. "Is d_8(tau^(2^8)) = 0?") and the 
boolean literals expected by the SAT solver.
It is responsible for assigning to each differential question
a unique integer (created in ascending order)
and for quickly returning the differential question associated
to the given literal representation.
"""

from .differential import Differential

class LiteralManager:
    """
    A class to manage the translation between differential questions
    and boolean literals for a SAT solver.
    """

    differentials: list[Differential]
    differentials_to_ids: dict[Differential, int]

    def __init__(self):
        """
        Initializes the LiteralManager with empty lists and dictionaries.
        """
        self.differentials = []
        self.differentials_to_ids = {}

    def add_differential(self, differential: Differential) -> int:
        """
        Adds a new differential question to the manager and returns its unique ID.
        If the differential already exists, returns its existing ID.

        Args:
            differential (Differential): The differential question to add.
        Returns:
            int: The unique ID assigned to the differential question.
        """
        if differential in self.differentials_to_ids:
            return self.differentials_to_ids[differential]
        else:
            new_id = len(self.differentials)
            self.differentials.append(differential)
            self.differentials_to_ids[differential] = new_id
            return new_id

    def get_differential_id(self, differential: Differential) -> int | None:
        """
        Retrieves the unique ID for a given differential question.

        Args:
            differential (Differential): The differential question to look up.
        Returns:
            int | None: The unique ID of the differential question, or None if it doesn't exist
        """
        return self.differentials_to_ids.get(differential, None)

    def get_differential_by_id(self, id: int) -> Differential | None:
        """
        Retrieves the differential question associated with a given ID.

        Args:
            id (int): The unique ID of the differential question. This also accepts the *negative* of the ID, which corresponds to the negation of the differential question.
        Returns:
            Differential | None: The differential question associated with the ID, or None if it doesn't exist
        """
        id = abs(id)
        if 0 <= id < len(self.differentials):
            return self.differentials[id]
        else:
            return None

