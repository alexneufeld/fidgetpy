import pytest
from fidgetpy import Vec2, Vec3, SwizzleError


def test_operations():
    a = Vec3(1, 2, 3)
    b = Vec3(4, 5, 6)
    c = Vec3(1 + 4, 2 + 5, 3 + 6)
    d = Vec3(-1, 2, 3)
    # elementwise equality
    assert a + b == c
    assert a != d
    # broadcast operations
    assert a / 3 == Vec3(1 / 3, 2 / 3, 3 / 3)
    # elementwise operations
    assert (a / b) == Vec3(1 / 4, 2 / 5, 3 / 6)
    # cross product
    assert a.cross(b) == Vec3(-3, 6, -3)
    # dot prodcut
    assert a.dot(b) == 32


def test_vec_creation():
    with pytest.raises(TypeError):
        Vec2(1)
    with pytest.raises(TypeError):
        Vec3(1, 2, 3, 4)


def test_swizzle():
    a = Vec3(1, 2, 3)
    # element access
    assert a.x == 1
    # swizzling
    assert a.xy == Vec2(1, 2)
    with pytest.raises(SwizzleError):
        _ = a.w
