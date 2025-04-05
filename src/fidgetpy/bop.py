from fidgetpy._core import Tree
from .vmath import min_, max_
import functools

def union(base: Tree, tool: Tree) -> Tree:
    return min_(base, tool)

def intersection(base: Tree, tool: Tree) -> Tree:
    return max_(base, tool)


def cut(base: Tree, tool: Tree) -> Tree:
    return max_(base, -tool)


def xor(base: Tree, tool: Tree) -> Tree:
    return min_(max_(base, -tool), max_(-base, tool))


def n_op(fn, commutative=True):
    def n_fn(*args) -> Tree:
        if len(args) == 1 and isinstance(args[0], (list, tuple)):
            if commutative:
                objs = args[0]
                if len(objs) == 1:
                    return objs[0]
                if len(objs) == 2:
                    return fn(objs[0], objs[1])
                if len(objs) > 2:
                    half = len(objs) // 2
                    return fn(
                        n_fn(objs[half:]),
                        n_fn(objs[:half])
                    )
            else:
                return functools.reduce(fn, objs)
        elif len(args) == 2 and isinstance(args[0], Tree) and isinstance(args[1], Tree):
            return fn(*args)
        else:
            errmsg = f"incorrect arguments to {fn}: {args}"
            raise RuntimeError(errmsg)
    return n_fn

union = fuse = n_op(union)
intersection = common = n_op(intersection)
difference = cut = n_op(cut, commutative=False)
xor = n_op(xor)
