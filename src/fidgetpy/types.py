import math
import operator
import functools
import itertools
from dataclasses import dataclass
from numbers import Real
from typing import Callable, Self
from .errors import (
    UnaryVectorCreationError,
    CrossProductError,
    VectorLengthMismatchError,
    SwizzleError,
    ShapeBoundsWarning,
)

from fidgetpy._core import Tree, Mesh


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
            return math.sqrt(squared)
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


@dataclass(frozen=True)
class BoundBox:
    """
    A rectangular volume in 3D space, represented by the x,y,z
    coordinates of its opposite corners.
    """

    xmin: Real
    xmax: Real
    ymin: Real
    ymax: Real
    zmin: Real
    zmax: Real

    @property
    def xlength(self) -> Real:
        return self.xmax - self.xmin

    @property
    def ylength(self) -> Real:
        return self.ymax - self.ymin

    @property
    def zlength(self) -> Real:
        return self.zmax - self.zmin

    @property
    def center(self) -> Vec3:
        return (
            Vec3(self.xmin, self.ymin, self.zmin)
            + Vec3(self.xmax, self.ymax, self.zmax)
        ) / 2

    @property
    def diagonal_length(self) -> Real:
        return (
            Vec3(self.xmax, self.ymax, self.zmax)
            - Vec3(self.xmin, self.ymin, self.zmin)
        ).length()


@dataclass(frozen=True)
class Shape:
    """
    A 2D or 3D solid shape, represented by an implicit mathematical
    expression (implicit distance field). This class implements
    semi-automatic tracking of its bounding box, enabling optimal
    evaluation and meshing in most cases.
    """

    tree: Tree
    bounds: BoundBox

    def eval(self, x, y, z):
        return self.tree.eval(x, y, z)

    def mesh(self, depth):
        # create an adjusted bounding box to compensate for infinite shapes
        bb = BoundBox(
            self.bounds.xmin if math.isfinite(self.bounds.xmin) else -1.0,
            self.bounds.xmax if math.isfinite(self.bounds.xmax) else 1.0,
            self.bounds.ymin if math.isfinite(self.bounds.ymin) else -1.0,
            self.bounds.ymax if math.isfinite(self.bounds.ymax) else 1.0,
            self.bounds.zmin if math.isfinite(self.bounds.zmin) else -1.0,
            self.bounds.zmax if math.isfinite(self.bounds.zmax) else 1.0,
        )
        if bb != self.bounds:
            raise ShapeBoundsWarning(
                "Shape has at least one non-finite bounding box face, "
                "mesh output may be truncated."
                f" Original bounding box: {self.bounds}"
            )
        # rescale the shape so that it fits inside a bounding box of [-1, 1]
        # on all axis
        sf = 1.01 * max(bb.xlength, bb.ylength, bb.zlength)
        mesh = self.tree.mesh(depth, *bb.center, sf)
        return mesh


__all__ = [
    "BoundBox",
    "Mesh",
    "Shape",
    "Tree",
    "Vec2",
    "Vec3",
    "Vec4",
    "Vector",
]
