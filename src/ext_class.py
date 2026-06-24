import find_differential
from .find_differential import element_degree

class ExtClass:
    def __init__(self, name: str, stem: int, adams_filtration: int, weight: int):
        self.name = 
        self.stem = stem
        self.adams_filtration = adams_filtration
        self.weight = weight

    def get_name(self) -> str:
        return self.name

    def get_degree(self) -> tuple[int, int, int]:
        return (self.stem, self.adams_filtration, self.weight)

    def get_differential_targets(self, r: int) -> list[ExtClass]:
        if self._ext is None:
            return []
        return self._ext.get_possible_differential_targets(self, r)

    def __add__(self, other: ExtClass) -> ExtClass:
        if self.get_degree() != other.get_degree():
            raise ValueError("Can only add Ext classes in the same tridegree")
        return ExtClass(
            f"{self.name} + {other.name}",
            self.stem,
            self.adams_filtration,
            self.weight,
            min(self.tautorsion, other.tautorsion),
            self._ext,
        )

    def __mul__(self, other: ExtClass) -> ExtClass:
        return ExtClass(
            f"{self.name} {other.name}",
            self.stem + other.stem,
            self.adams_filtration + other.adams_filtration,
            self.weight + other.weight,
            min(self.tautorsion, other.tautorsion),
            self._ext,
        )

    def get_name_latex(self) -> str:
        return self.name.replace("tau", r"\tau").replace("rho", r"\rho")

    def __hash__(self) -> int:
        return hash((self.name, self.get_degree()))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ExtClass):
            return False
        return self.name == other.name and self.get_degree() == other.get_degree()

    def __repr__(self) -> str:
        return f"ExtClass({self.name!r}, degree={self.get_degree()})"
