from .differential import Differential, UNDEFINED
from .ext import Ext
from .literal_manager import LiteralManager
from pysat.solvers import Gluecard4

class SATSolver:
    E1_page: Ext
    literal_manager: LiteralManager
    max_coweight: int

    def __init__(self, E1_page: Ext, max_coweight: int):
        self.E1_page = E1_page
        self.literal_manager = LiteralManager()
        if max_coweight < 0:
            raise ValueError("max_coweight must be non-negative")
        self.max_coweight = max_coweight

    def create_literals(self):
        classes = self.E1_page.get_classes_up_to_coweight(self.max_coweight)
        for ext_class in classes:
            pass


