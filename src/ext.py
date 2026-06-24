from .ext_class import ExtClass
from .differential import Differential
from .find_differential import get_classes  

class Ext:
    def __init__(self, coweight, tridegree, classes, differentials):
        self.coweight = coweight
        self.tridegree = tridegree
        self.classes = classes['stem']
        self.differentials = differentials


    def get_classes_up_to_coweight(self, coweight: int) -> list[ExtClass]:
        pass

    def get_classes_in_fixed_degree(self, N: int) -> list[ExtClass]:
        pass

    def get_classes_in_tridegree(self, tridegree: tuple[int, int, int]) -> list[ExtClass]:
        pass

    def get_rho_periodic_elements(self) -> list[ExtClass]:
        pass

    def is_rho_periodic(self, ext_class: ExtClass) -> bool:
        pass

    def get_h1_periodic_elements(self) -> list[ExtClass]:
        pass

    def is_h1_periodic(self, ext_class: ExtClass) -> bool:
        pass

    def get_known_differentials(self) -> list[Differential]:
        pass

