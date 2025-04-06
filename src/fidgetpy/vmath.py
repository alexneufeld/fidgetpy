import functools
import operator
import math
from fidgetpy._core import Tree
from numbers import Real
from typing import Callable
from .vec import Vector


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
