from numbers import Real
from fidgetpy._core import Tree
from .vec import Vec3, axes
from dataclasses import dataclass


@dataclass(init=False, frozen=True)
class BoundBox:
    def __init__(self, *args) -> None:
        if len(args) == 6:  # 6 floats
            xmin, xmax, ymin, ymax, zmin, zmax = args
        elif len(args) == 2:  # 2 vectors
            xmin, ymin, zmin = args[0]
            xmax, ymax, zmax = args[1]
        elif len(args) == 1:  # another boundbox
            pass
        _min = Vec3(
            min(xmin, xmax),
            min(ymin, ymax),
            min(zmin, zmax),
        )
        _max = Vec3(
            max(xmin, xmax),
            max(ymin, ymax),
            max(zmin, zmax),
        )
        object.__setattr__(self, "_min", _min)
        object.__setattr__(self, "_max", _max)

    @property
    def xmin(self) -> Real:
        return self._min.x

    @property
    def xmax(self) -> Real:
        return self._max.x

    @property
    def ymin(self) -> Real:
        return self._min.y

    @property
    def ymax(self) -> Real:
        return self._max.y

    @property
    def zmin(self) -> Real:
        return self._min.z

    @property
    def zmax(self) -> Real:
        return self._max.z

    @property
    def xlength(self) -> Real:
        return self._max.x - self._min.x

    @property
    def ylength(self) -> Real:
        return self._max.y - self._min.y

    @property
    def zlength(self) -> Real:
        return self._max.z - self._min.z

    @property
    def center(self) -> Vec3:
        return (self._max + self._min) / 2

    @property
    def diagonal_length(self) -> Real:
        return (self._max - self._min).length()


@dataclass(frozen=True)
class Shape:
    tree: Tree
    boundbox: BoundBox

    def mesh(self, depth):
        return self.tree.mesh(depth)

    def eval(self, x, y, z):
        return self.tree.eval(x, y, z)


def sphere(r=1.0) -> Shape:
    """
    A sphere with radius r, centerered at the origin
    """
    return Shape(axes().length() - r, BoundBox(-r, -r, -r, r, r, r))


def box(xlen, ylen, zlen):
    return None


def translate(shp: Shape, mov: Vec3) -> Shape:
    return Shape(
        shp.tree.remap_xyz(*(axes - mov)),
        BoundBox(shp.boundbox._min + mov, shp.boundbox._max + mov),
    )
