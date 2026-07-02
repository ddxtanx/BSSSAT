"""
This file contains utility functions for converting Ext element names to LaTeX format that
are valid for the Adams-motivic-E2.csv file. It does not translate the machine names.
"""


import re


def convert_to_latex(name: str) -> str:
    """Convert an Ext element name string into LaTeX."""
    token_re = re.compile(
        r"(?P<body>[A-Za-z][A-Za-z0-9]*(?:,[0-9]+)?)(?P<prime>'+)?"
        r"(?:_(?P<sub>[A-Za-z0-9,']+))?(?:\^(?P<sup>[A-Za-z0-9+-]+))?"
    )
    greek = {
        "tau": r"\tau",
        "rho": r"\rho",
    }

    def format_token(match: re.Match[str]) -> str:
        body = match.group("body")
        prime = match.group("prime")
        sub = match.group("sub")
        sup = match.group("sup")
        base = body

        if sub is None:
            trailing_digits = re.fullmatch(r"([A-Za-z]+)([0-9]+(?:,[0-9]+)?)", body)
            if trailing_digits:
                base = trailing_digits.group(1)
                sub = trailing_digits.group(2)

        latex = greek.get(base, base)

        if sub is not None:
            latex += f"_{{{sub}}}"

        superscript = ""
        if prime is not None:
            superscript += r"\prime" * len(prime)
        if sup is not None:
            superscript += sup
        if superscript:
            latex += f"^{{{superscript}}}"

        return latex

    pieces = []
    for piece in re.split(r"(\s*\+\s*)", name.strip()):
        if "+" in piece:
            pieces.append(piece)
            continue

        factors = piece.split()
        if len(factors) > 1:
            factors = [factor for factor in factors if factor != "1"]
            piece = " ".join(factors) if factors else "1"
        pieces.append(piece)
    name = "".join(pieces)

    latex_name = token_re.sub(format_token, name)
    latex_name = re.sub(r"\s*\+\s*", " + ", latex_name)
    latex_name = re.sub(r"\s+", " ", latex_name)
    return latex_name.strip()



