import csv
from pathlib import Path
from typing import Any, Iterable

from .ext_class import ExtClass
from .differential import Differential

class Ext:
    DEFAULT_CLASSES_PATH = Path(__file__).resolve().parents[1] / "ext_data" / "Adams-motivic-E2.csv"

    def __init__(
        self,
        classes: Iterable[ExtClass | dict[str, Any]] | None = None,
        classes_path: str | Path | None = None,
    ) -> None:
        if classes is None:
            classes = self._read_classes_csv(classes_path or self.DEFAULT_CLASSES_PATH)
        self.classes = [self._as_ext_class(ext_class) for ext_class in classes]

    def get_classes(self) -> list[ExtClass]:
        return list(self.classes)

    def get_classes_up_to_coweight(self, coweight: int) -> list[ExtClass]:
        return [
            ext_class
            for ext_class in self.classes
            if ext_class.stem - ext_class.weight <= coweight
        ]

    def get_classes_in_fixed_degree(self, N: int) -> list[ExtClass]:
        return [
            ext_class
            for ext_class in self.classes
            if ext_class.stem + ext_class.adams_filtration - ext_class.weight == N
        ]

    def get_classes_in_tridegree(self, tridegree: tuple[int, int, int]) -> list[ExtClass]:
        return [
            ext_class
            for ext_class in self.classes
            if ext_class.get_degree() == tridegree
        ]

    def get_possible_differential_targets(self, source: ExtClass, r: int) -> list[ExtClass]:
        target_degree = (
            source.stem + r - 1,
            source.adams_filtration + 1,
            source.weight + r,
        )
        return self.get_classes_in_tridegree(target_degree)

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

    def _read_classes_csv(self, classes_path: str | Path) -> list[dict[str, str]]:
        with Path(classes_path).open(newline="") as csvfile:
            return list(csv.DictReader(csvfile))

    def _as_ext_class(self, ext_class: ExtClass | dict[str, Any]) -> ExtClass:
        if isinstance(ext_class, ExtClass):
            return ExtClass(
                ext_class.name,
                ext_class.stem,
                ext_class.adams_filtration,
                ext_class.weight,
                ext_class.tautorsion,
                self,
            )

        return ExtClass(
            str(ext_class["name"]),
            int(ext_class["stem"]),
            int(ext_class.get("adams_filtration", ext_class.get("Adams filtration"))),
            int(ext_class["weight"]),
            int(ext_class.get("tautorsion", 0)),
            self,
        )
