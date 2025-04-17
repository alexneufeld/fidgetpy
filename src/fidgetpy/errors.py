class ShapeBoundsWarning(RuntimeWarning):
    """Warn the user when a shape with a non-finite
    or otherwise messed up bounding box is rendered"""


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


__all__ = [
    "ShapeBoundsWarning",
    "VectorError",
    "UnaryVectorCreationError",
    "CrossProductError",
    "VectorLengthMismatchError",
    "SwizzleError",
]
