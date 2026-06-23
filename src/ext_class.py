import csv
from dataclasses import dataclass
from pathlib import Path


CSV_PATH = Path(__file__).with_name("Adams-motivic-E2.csv")


@dataclass
class Element:
    name: str
    stem: int
    adams_filtration: int
    weight: int
    tautorsion: int
    shift: int
    h0info: str
    h0target: str
    h1info: str
    h1target: str
    h2info: str
    h2target: str
    drinfo: str
    drtarget: str


def load_elements(csv_path=CSV_PATH):
    all_elements = []

    with open(csv_path, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            element = Element(
                name=row["name"],
                stem=int(row["stem"]),
                adams_filtration=int(row["Adams filtration"]),
                weight=int(row["weight"]),
                tautorsion=int(row["tautorsion"]),
                shift=int(row["shift"]),
                h0info=row["h0info"],
                h0target=row["h0target"],
                h1info=row["h1info"],
                h1target=row["h1target"],
                h2info=row["h2info"],
                h2target=row["h2target"],
                drinfo=row["drinfo"],
                drtarget=row["drtarget"],
            )
            all_elements.append(element)

    return all_elements


all_elements = load_elements()

print(f"Loaded {len(all_elements)} elements")

for element in all_elements:

    print(element)
