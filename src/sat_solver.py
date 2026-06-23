"""
Expected Interface:

- In ext_class.py, an implementation of classes in Ext_{\mathscr{A}^{\mathbb{C}}}(\mathbb{M}_{\mathbb{C}}, \mathbb{M}_{\mathbb{C}})
  including:
  - the class ExtClass
    with methods:
        - get_name(self) -> str
            which returns the string representation of the name of the element
        - get_degree(self) -> tuple[int, int, int]
            which return the motivic tridegree (s, f, w) of the element
        - get_differential_targets(self, r: int) -> list[ExtClass]
            which returns the list of elements (as ExtClass instances) that could possibly be targets of the differential d_r on this element
        - __add__(self, other: ExtClass) -> ExtClass
            which returns the sum of two ExtClass instances
        - __mul__(self, other: ExtClass) -> ExtClass
            which returns the product of two ExtClass instances
        - get_name_latex(self) -> str
            which returns the LaTeX representation of the name of the element

- In differential.py, an implementation of possible differentials in Ext 
  including:
    - a constant UNDEFINED representing an undefined differential (i.e. one applied to an element that was not a cycle on a previous page)
    - the class Differential
    with methods:
        - get_source(self) -> ExtClass
            which returns the source of the differential
        - get_target(self) -> ExtClass
            which returns the target of the differential
        - is_cycle(self) -> bool
            which returns True if the differential represents a cycle (i.e. the target is zero)
        - get_id(self) -> int
            which returns a unique integer identifier for use in representing the differential in the SAT solver
        - get_tridegree(self) -> tuple[int, int, int]
            which returns the motivic tridegree (s, f, w) of the differential [meant as a sanity check, should always be constant]
- In ext.py, an implementation of the entire Ext as a collection of ExtClasses
    including:
    - the class Ext
    with methods:
        - get_classes_up_to_coweight(self, coweight: int) -> list[ExtClass]
            which returns the list of classes in Ext up to a given s - w coweight
        - get_classes_in_fixed_degree(self, N: int) -> list[ExtClass]
            which returns the list of classes whose "fixed degree" s + f - w equals N
        - get_classes_in_tridegree(self, tridegree: tuple[int, int, int]) -> list[ExtClass]
            which returns the list of classes in a given motivic tridegree (s, f, w)
"""
