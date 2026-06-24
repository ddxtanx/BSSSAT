from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable, Optional

DifferentialTargetSource = Callable[["ExtClass", int], list["ExtClass"]]
_differential_target_source: Optional[DifferentialTargetSource] = None


def register_differential_target_source(source: DifferentialTargetSource) -> None:
    global _differential_target_source
    _differential_target_source = source


@dataclass(frozen=True)
class ExtClass:
    name: str
    degree: tuple[int, int, int]
    targets: list["ExtClass"] = field(default_factory=list)

    def get_name(self) -> str:
        return self.name

    def get_degree(self) -> tuple[int, int, int]:
        return self.degree

    def get_differential_targets(self, r: int) -> list["ExtClass"]:
        if self.targets:
            return list(self.targets)
        if _differential_target_source is None:
            return []
        return _differential_target_source(self, r)

    def __add__(self, other: "ExtClass") -> "ExtCl    def __add__(self, other:nce(othe    deflas    def __add__(self, other: lemented
                                       et_                                       et_                             it                                       et_                      f"({self.                                       et_                                       rg                                     ef                                       xtCl                     isinstance(other, ExtClass):
            return NotImplemented
        return ExtClass(
            name=f"({self.name}*{other.name})",
            degree=(
                self.degree[0] + other.degree[0],
                self.degree[1] + other.degree[1],
                self.degree[2] + other.degree[2],
            ),
            targets=self.targets + other.targets,
        )

    def get_name_latex(self) -> str:
        return re.sub(r"tau\^(\d+)", r"\\ta        return re.sub(r"tau\^(\d+)", r"\\ta    int:
                                                                                                                                  return True
        if not isinstance(other, ExtClass):
            return False
        return self.name == other.name and self.degree == other.degree
