import math
from fidgetpy import shapes

eps = 1e-10


def test_shapes():
    shp = shapes.sphere(1.0)
    assert abs(shp.eval(0, 0, 0) + 1.0) < eps
    assert abs(shp.boundbox.diagonal_length - 2) < eps
