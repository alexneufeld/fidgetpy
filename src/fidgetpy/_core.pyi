from typing import Self

class FidgetError(Exception):
    """Wrapper around internal fidget library errors."""

class Mesh:
    """A triangle mesh, represented by a list of vertices
    (3-tuples of xyz coordinates), and a list of triangles
    (3-tuples of indexes into the vertices list).
    """

    vertices: list[tuple[float, float, float]]
    triangles: list[tuple[int, int, int]]

    def to_stl(self) -> bytes:
        """Convert to a binary stl"""
        ...

class Tree:
    """A tree structure of arbitrary mathematical operations."""

    @staticmethod
    def x() -> Self:
        """Returns a tree representing the x axis variable."""
        ...

    @staticmethod
    def y() -> Self:
        """Returns a tree representing the y axis variable."""
        ...

    @staticmethod
    def z() -> Self:
        """Returns a tree representing the z axis variable."""
        ...

    @staticmethod
    def var() -> Self:
        """Returns a tree representing an arbitrary anonymous variable."""
        ...

    @staticmethod
    def constant(f: float) -> Self:
        """Returns a tree representing a fixed floating point value."""
        ...

    def eval(self, x: float, y: float, z: float) -> float:
        """evaluate this tree at a single point in 3D space
        This is not efficient, and mostly useful for basic tests."""
        ...

    def eval_map(self, varmap: dict[Self:float]) -> float:
        """Evaluate this tree using a single value for each xyz or anonymous variable."""
        ...

    def remap_xyz(self, new_x: Self, new_y: Self, new_z: Self) -> Self:
        """Transform this tree by replacing the underlying xyz nodes."""
        ...

    def deriv(self, v: Self, n: int) -> Self:
        """Compute a tree representing the n-th derivative of this tree
        with respect to the given variable."""
        ...

    def from_vm(self, src: str) -> Self:
        """Build a tree from a simple SSA tape text representation."""
        ...

    def to_vm(self) -> str:
        """Convert a tree to a simple SSA tape text representation."""
        ...

    def to_graphviz(self) -> str:
        """Pretty print a tree to graphviz (dot language syntax)."""
        ...

    def square(self) -> Self:
        """Returns a tree that calculates the square of its input. Equivalent to thisnode**2."""
        ...

    def floor(self) -> Self:
        """Returns a tree that calculates the floor of its input."""
        ...

    def recip(self) -> Self:
        """Returns a tree that calculates the reciprocal value of its input (1/x)."""
        ...

    def ceil(self) -> Self:
        """Returns a tree that calculates the ceil of its input."""
        ...

    def round(self) -> Self:
        """Returns a tree that rounds its input to the nearest whole number."""
        ...

    def sqrt(self) -> Self:
        """Returns a tree that calculates the sqrt of its input."""
        ...

    def neg(self) -> Self:
        """Returns a tree that negates its input."""
        ...

    def sin(self) -> Self:
        """Returns a tree that calculates the sin of its input."""
        ...

    def cos(self) -> Self:
        """Returns a tree that calculates the cosine of its input."""
        ...

    def tan(self) -> Self:
        """Returns a tree that calculates the tangent of its input."""
        ...

    def asin(self) -> Self:
        """Returns a tree that calculates the arc-sine of its input."""
        ...

    def acos(self) -> Self:
        """Returns a tree that calculates the arc-cosine of its input."""
        ...

    def atan(self) -> Self:
        """Returns a tree that calculates the arc-tangent of its input."""
        ...

    def exp(self) -> Self:
        """Returns a tree that calculates the exponent of its input (e**x)."""
        ...

    def ln(self) -> Self:
        """Returns a tree that calculates the natural logarithm of its input."""
        ...

    def not_(self) -> Self:
        """Returns a tree that performs ligical negation on its input
        The output is 1 if the input is 0, and 0 otherwise."""
        ...

    def abs(self) -> Self:
        """Returns a tree that calculates the absolute value of its input."""
        ...

    def pow(self, other: Self | float) -> Self:
        """Returns a tree that raises its input to an arbitrary integer power.
        Pythons '**' operator is equivalent to this"""
        ...

    def add(self, other: Self | float) -> Self:
        """Returns a tree that adds its children.
        the '+' operator may also be used on trees"""
        ...

    def sub(self, other: Self | float) -> Self:
        """Returns a tree that calculates the difference between its children.
        the '-' operator may also be used on trees"""
        ...

    def mul(self, other: Self | float) -> Self:
        """Returns a tree that calculates the product of its children.
        the '*' operator may also be used on trees"""
        ...

    def div(self, other: Self | float) -> Self:
        """Returns a tree that performs floating point division on its children.
        the '/' operator may also be used on trees"""
        ...

    def max(self, other: Self | float) -> Self:
        """Returns a tree that finds the maximum of two input values.
        tree1.max(tree2) is equivalent to max(tree1, tree2)."""
        ...

    def min(self, other: Self | float) -> Self:
        """returns a tree that finds the minimum of two input values.
        tree1.min(tree2) is equivalent to min(tree1, tree2)."""
        ...

    def compare(self, other: Self | float) -> Self:
        """returns a tree that compares two values.
        The result is -1 if a < b, +1 if a > b, 0 if a == b, and NaN if either side is NaN."""
        ...

    def modulo(self, other: Self | float) -> Self:
        """returns a tree that performs modulo division.
        tree1.modulo(tree2) is equivalent to tree1 % tree2."""
        ...

    def and_(self, other: Self | float) -> Self:
        """Returns a tree that performs a logical and operation.
        If both arguments are non-zero, returns the right-hand argument.
        Otherwise, returns zero."""
        ...

    def or_(self, other: Self | float) -> Self:
        """Returns atree that performs a logical or operation.
        If the left-hand argument is non-zero, it is returned.
        Otherwise, the right-hand argument is returned."""
        ...

    def atan2(self, other: Self | float) -> Self:
        """Returns a tree that implements the two argument arc-tangent function.
        tree1.atan2(tree2) is equivalent to Tree.atan(tree2/tree1)."""
        ...
