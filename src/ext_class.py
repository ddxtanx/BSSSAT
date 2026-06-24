class ExtClass:
    def get_name(self) -> str:
        pass

    def get_degree(self) -> tuple[int, int, int]:
        pass

    def get_differential_targets(self, r: int) -> list[ExtClass]:
        pass

    def __add__(self, other: ExtClass) -> ExtClass:
        pass

    def __mul__(self, other: ExtClass) -> ExtClass:
        pass

    def get_name_latex(self) -> str:
        pass

    def __hash__(self) -> int:
        pass

    def __eq__(self, other: object) -> bool:
        pass
