from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Callable


DATA_PATH = Path(__file__).with_name("Adams-motivic-E2-machine.csv")
TAU_PREFIX_RE = re.compile(r"^\s*tau(?:\^(\d+))?\s+(.+?)\s*$")


def tau_exponent(name: str) -> int:
    """Return the exponent n from a name like 'tau^n x'."""
    match = TAU_PREFIX_RE.match(name)
    if not match:
        return 0
    exponent = match.group(1)
    return int(exponent) if exponent is not None else 1


def remove_tau_from_name(name: str) -> str:
    """Return the generator name after removing a leading tau power."""
    match = TAU_PREFIX_RE.match(name)
    if not match:
        return name.strip()
    return match.group(2).strip()


def _name_with_tau(name: str, exponent: int) -> str:
    if name == "0":
        return "0"
    if exponent == 0:
        return name
    return f"tau^{exponent} {name}"


def _load_classes_by_name() -> dict[str, dict[str, int | str]]:
    classes_by_name: dict[str, dict[str, int | str]] = {}
    with DATA_PATH.open(newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            classes_by_name[row["name"]] = {
                "name": row["name"],
                "stem": int(row["stem"]),
                "Adams filtration": int(row["Adams filtration"]),
                "weight": int(row["weight"]),
                "tautorsion": int(row["tautorsion"]),
            }
    return classes_by_name


CLASSES_BY_NAME = _load_classes_by_name()


def zero_element(stem: int, adams_filtration: int, weight: int) -> dict[str, int | str]:
    return {
        "name": "0",
        "stem": stem,
        "Adams filtration": adams_filtration,
        "weight": weight,
        "tautorsion": 0,
    }


def look_up_element_by_machine_name(machine_name: str) -> dict[str, int | str]:
    """
    Look up an element by machine name, allowing a leading tau power.

    In the CSV convention, tautorsion == 0 means tau-torsion-free. A finite
    tau-torsion class is killed only when the tau exponent reaches its torsion.
    """
    machine_name_without_tau = remove_tau_from_name(machine_name)
    degree_of_tau = tau_exponent(machine_name)

    if machine_name_without_tau == "0":
        raise ValueError("The zero element needs an explicit tridegree")

    if machine_name_without_tau not in CLASSES_BY_NAME:
        raise ValueError(f"{machine_name_without_tau!r} is not in {DATA_PATH.name}")

    element_without_tau = CLASSES_BY_NAME[machine_name_without_tau]
    tautorsion = int(element_without_tau["tautorsion"])
    weight = int(element_without_tau["weight"]) - degree_of_tau

    if tautorsion > 0 and degree_of_tau >= tautorsion:
        return zero_element(
            int(element_without_tau["stem"]),
            int(element_without_tau["Adams filtration"]),
            weight,
        )

    remaining_tautorsion = 0 if tautorsion == 0 else tautorsion - degree_of_tau
    return {
        "name": _name_with_tau(machine_name_without_tau, degree_of_tau),
        "stem": int(element_without_tau["stem"]),
        "Adams filtration": int(element_without_tau["Adams filtration"]),
        "weight": weight,
        "tautorsion": remaining_tautorsion,
    }


def product(element1: str, element2: str) -> list[str]:
    """
    Placeholder for the ordinary product of module generators.

    Replace this with your teammate's function. It should take two strings with
    no leading tau powers and return a list of generator-name strings.
    """
    raise NotImplementedError("product(element1, element2) has not been implemented yet")




def product_of_tau_multiple(
    element1: str,
    element2: str,
    product_function: Callable[[str, str], list[str]] | None = None,
) -> tuple[tuple[int, int, int], list[str]]:
    """
    Multiply two possibly tau-multiplied module generators.

    For example, this reduces (tau^2 x) * (tau^3 y) to
    tau^5 * product(x, y). The return value is (degree, names), ready to pass
    into vector_by_basis_names(degree, names). If the result is zero, names is
    the empty list.
    """
    element1_tau_exponent = tau_exponent(element1)
    element2_tau_exponent = tau_exponent(element2)
    element1_without_tau = remove_tau_from_name(element1)
    element2_without_tau = remove_tau_from_name(element2)
    element1_without_tau_info = look_up_element_by_machine_name(element1_without_tau)
    element2_without_tau_info = look_up_element_by_machine_name(element2_without_tau)

    if product_function is None:
        product_function = product

    product_tau_exponent = element1_tau_exponent + element2_tau_exponent
    product_degree = (
        int(element1_without_tau_info["stem"]) + int(element2_without_tau_info["stem"]),
        int(element1_without_tau_info["Adams filtration"])
        + int(element2_without_tau_info["Adams filtration"]),
        int(element1_without_tau_info["weight"])
        + int(element2_without_tau_info["weight"])
        - product_tau_exponent,
    )
    product_names = product_function(element1_without_tau, element2_without_tau)
    if not product_names:
        return product_degree, []

    result_names: list[str] = []
    for product_name in product_names:
        product_name_without_tau = remove_tau_from_name(product_name)
        if product_name_without_tau == "0":
            continue

        name_with_tau = _name_with_tau(product_name_without_tau, product_tau_exponent)
        element = look_up_element_by_machine_name(name_with_tau)

        if element["name"] == "0":
            continue
        else:
            result_names.append(str(element["name"]))

    return product_degree, result_names
