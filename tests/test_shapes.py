import math
from fidgetpy import shapes

eps = 1e-10


def test_shapes():
    shp = shapes.sphere(1.0)
    assert abs(shp.eval(0, 0, 0) + 1.0) < eps
    assert abs(shp.bounds.diagonal_length - math.sqrt(12)) < eps


def test_meshing_and_stuff():
    s = shapes.sphere(1.0)
    s = shapes.move(s, 1, 1, 1)
    s2 = shapes.box(2, 2, 2)
    s3 = shapes.difference(s, s2)
    m = s3.mesh(5)
    assert len(m.vertices) > 1000
    assert len(m.triangles) > 1000


def test_torus():
    s = shapes.torus(2.0, 1.0)
    m = s.mesh(5)
    assert len(m.vertices) > 1000
    assert len(m.triangles) > 1000


def test_cylinder():
    s = shapes.cylinder(0.5, 0.6)
    s = shapes.move(s, 0.5, 0.5, 0.5)
    m = s.mesh(5)
    assert len(m.vertices) > 1000
    assert len(m.triangles) > 1000


def test_revolve():
    s = shapes.circle(1)
    s = shapes.move(s, 2, 1, 0)
    s = shapes.revolve_z(s)
    m = s.mesh(5)
    assert len(m.vertices) > 1000
    assert len(m.triangles) > 1000


def test_extrude():
    s = shapes.circle(1)
    s = shapes.extrude_z(s, 1.0)
    m = s.mesh(5)
    assert len(m.vertices) > 1000
    assert len(m.triangles) > 1000
