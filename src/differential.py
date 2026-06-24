UNDEFINED = -1
class Differential:
    def get_source(self) -> ExtClass:
        pass

    def get_target(self) -> ExtClass:
        pass

    def is_cycle(self) -> bool:
        pass

    def get_id(self) -> int:
        pass

    def get_tridegree(self) -> tuple[int, int, int]:
        pass
