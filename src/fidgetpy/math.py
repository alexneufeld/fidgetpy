import math
import operator
import functools
import itertools
from dataclasses import dataclass
from numbers import Real
from typing import Callable, Self
from fidgetpy._core import Tree, Mesh


class VectorError(Exception):
    """Base class for errors related to vectors"""


class UnaryVectorCreationError(VectorError):
    """Don't create one element vectors"""


class CrossProductError(VectorError):
    """The cross product is only possible with vec3s"""


class VectorLengthMismatchError(VectorError):
    """Can only do elementwise operations on vectors of equal length"""


class SwizzleError(VectorError):
    """Usually caused by invalid indexes in swizzle operations"""


@dataclass(init=False, frozen=True)
class Vector:
    """
    Base class for vector types that can mix numbers and implicit expressions
    """

    _items: list[Real | Tree]

    def __init__(self, *args):
        if len(args) < 2:
            raise UnaryVectorCreationError("Don't create vectors of length one")
        if not all(isinstance(x, (Real, Tree)) for x in args):
            raise ValueError("Can only create Vectors of Trees or real numbers")
        # self._items = args
        object.__setattr__(self, "_items", args)

    def __getattr__(self, val: str) -> Self | Real | Tree:
        if not set(val) <= set("xyzw"):
            raise AttributeError(f"'Vec{len(self)}' object has no attribute '{val}'")
        if not set(val) <= set("xyzw"[: len(self)]):
            raise SwizzleError(f"invalid index for 'Vec{len(self)}' object: '{val}'")

        def lookup(p):
            return self._items[ord(p) % 4]

        # don't return a vector in the case of e.g.: myvec.x
        if len(val) == 1:
            return lookup(val)
        # swizzle :)
        return Vector(*map(lookup, val))

    def __iter__(self):
        return (x for x in self._items)

    def __len__(self) -> int:
        return len(self._items)

    def dot(self, other) -> Real | Tree:
        return functools.reduce(operator.add, self * other)

    def cross(a, b) -> Self:
        if not len(a) == 3 and not len(b) == 3:
            raise CrossProductError(
                "The cross product is only defined for vectors of length 3"
            )
        return Vec3(
            a.y * b.z - a.z * b.y,
            a.z * b.x - a.x * b.z,
            a.x * b.y - a.y * b.x,
        )

    def length(self) -> Real | Tree:
        squared = functools.reduce(operator.add, self**2)
        if isinstance(squared, Real):
            return sqrt(squared)
        elif isinstance(squared, Tree):
            return squared.sqrt()

    def normalize(self) -> Real | Tree:
        return self / self.length()

    @staticmethod
    def _broadcast_bop(fn, a, b, swap=False) -> Self:
        if swap:
            return Vector(*itertools.starmap(fn, zip(itertools.repeat(b, len(a)), a)))
        else:
            return Vector(*itertools.starmap(fn, zip(a, itertools.repeat(b, len(a)))))

    @staticmethod
    def _elementwise_bop(fn, a, b) -> Self:
        if not len(a) == len(b):
            raise VectorLengthMismatchError(
                "Can't perform an element-wise operation on vectors of different lengths"
            )
        return Vector(*itertools.starmap(fn, zip(a, b, strict=True)))

    @staticmethod
    def _binary_op(fn, swap=False) -> Callable:
        def method(self, other):
            if isinstance(other, Vector):  # elementwise operation
                if swap:
                    return self._elementwise_bop(fn, other._items, self._items)
                else:
                    return self._elementwise_bop(fn, self._items, other._items)
            else:  # broadcast operation
                if swap:
                    return self._broadcast_bop(fn, self, other, True)
                else:
                    return self._broadcast_bop(fn, self, other)

        return method

    @staticmethod
    def _unary_op(fn) -> Callable:
        def method(self):
            return Vector(*map(fn, self._items))

        return method

    __add__ = __radd__ = _binary_op(operator.add)
    __sub__ = _binary_op(operator.sub)
    __rsub__ = _binary_op(operator.sub, True)
    __mul__ = __rmul__ = _binary_op(operator.mul)
    __truediv__ = _binary_op(operator.truediv)
    __rtruediv__ = _binary_op(operator.truediv, True)
    __mod__ = _binary_op(operator.mod)
    __rmod__ = _binary_op(operator.mod, True)
    __pow__ = _binary_op(operator.pow)
    __rpow__ = _binary_op(operator.pow, True)
    __neg__ = _unary_op(operator.neg)
    __abs__ = _unary_op(abs)
    __round__ = _unary_op(round)

    def __repr__(self) -> str:
        return f"Vec{len(self._items)}{self._items}"


def Vec2(x, y):
    return Vector(x, y)


def Vec3(x, y, z):
    return Vector(x, y, z)


def Vec4(x, y, z, w):
    return Vector(x, y, z, w)


_x = Tree.x()
_y = Tree.y()
_z = Tree.z()


def axes() -> Vec3:
    return Vec3(_x, _y, _z)


def axes2d() -> Vec2:
    return Vec2(_x, _y)


def recursive_fn(numeric_fn: Callable, nodal_fn: str) -> Callable:
    def my_fn(arg):
        if isinstance(arg, Tree):
            return getattr(arg, nodal_fn)()
        elif isinstance(arg, Real):
            return numeric_fn(arg)
        elif isinstance(arg, Vector):
            return Vector(*(my_fn(x) for x in arg))

    return my_fn


sqrt = recursive_fn(math.sqrt, "sqrt")
sin = recursive_fn(math.sin, "sin")
cos = recursive_fn(math.cos, "cos")
tan = recursive_fn(math.tan, "tan")
asin = recursive_fn(math.asin, "asin")
acos = recursive_fn(math.acos, "acos")
atan = recursive_fn(math.atan, "atan")
ln = recursive_fn(math.log, "ln")
exp = recursive_fn(math.exp, "exp")
abs_ = recursive_fn(abs, "abs")
round_ = recursive_fn(round, "round")
not_ = recursive_fn(lambda x: 1.0 if x == 0.0 else 0.0, "not")


def recursive_2arg_fn(numeric_fn: Callable, nodal_fn: str) -> Callable:
    def my_fn(a, b):
        # elementwise comparison returning a vector
        if isinstance(a, Vector) and isinstance(b, Vector):
            return Vector(*(my_fn(u, v) for u, v in zip(a, b)))
        # broadcast a scalar across a vector
        elif isinstance(a, Vector) and not isinstance(b, Vector):
            return Vector(*(my_fn(x, b) for x in a))
        elif not isinstance(a, Vector) and isinstance(b, Vector):
            return Vector(*(my_fn(a, x) for x in b))
        # compare 2 numbers
        elif isinstance(a, Real) and isinstance(b, Real):
            return numeric_fn(a, float(b))
        # compare Trees and numbers
        elif isinstance(a, Tree) and isinstance(b, Real):
            return getattr(a, nodal_fn)(b)
        elif isinstance(a, Real) and isinstance(b, Tree):
            return getattr(Tree.constant(a), nodal_fn)(b)
        elif isinstance(a, Tree) and isinstance(b, Tree):
            return getattr(a, nodal_fn)(b)

    return my_fn


max_ = recursive_2arg_fn(max, "max")
min_ = recursive_2arg_fn(min, "min")
atan2 = recursive_2arg_fn(math.atan2, "atan2")
compare = recursive_2arg_fn(
    lambda a, b: 0.0 if a == b else -1.0 if a < b else 1.0, "compare"
)
and_ = recursive_2arg_fn(lambda a, b: float(a and b), "and")
or_ = recursive_2arg_fn(lambda a, b: float(a or b), "or")


def lt(a, b):
    return max_(compare(b, a), 0.0)


def le(a, b):
    return min_(compare(b, a) + 1.0, 1.0)


def sum_(it):
    return functools.reduce(operator.add, it)


def length(v):
    return v.length()


def clamp(x, minimum, maximum):
    return max_(minimum, min_(x, maximum))


def smoothstep(edge0, edge1, x):
    # Scale, and clamp x to 0..1 range
    x = clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return x * x * (3.0 - 2.0 * x)


def mix(x, y, a):
    return x * (1.0 - a) + y * a


def dot(a, b):
    return a.dot(b)


def cross(a, b):
    return a.cross(b)


__all__ = [
    "Tree",
    "Mesh",
    "Vec2",
    "Vec3",
    "Vec4",
    "axes",
    "axes2d",
    "sqrt",
    "sin",
    "cos",
    "tan",
    "asin",
    "acos",
    "atan",
    "ln",
    "exp",
    "abs_",
    "round_",
    "not_",
    "lt",
    "le",
    "sum_",
    "length",
    "clamp",
    "smoothstep",
    "mix",
    "dot",
    "cross",
]
