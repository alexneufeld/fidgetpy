import pytest
from fidgetpy.types import Tree
from fidgetpy.errors import FidgetError

txt = """# This is a comment!
0x600000b90000 var-x
0x600000b900a0 square 0x600000b90000
0x600000b90050 var-y
0x600000b900f0 square 0x600000b90050
0x600000b90140 add 0x600000b900a0 0x600000b900f0
0x600000b90190 sqrt 0x600000b90140
0x600000b901e0 const 1
"""


def test_vm_import():
    s1 = Tree.from_vm(txt)
    assert len(s1) == 4
    incorrect = """addmul 1 2"""
    with pytest.raises(FidgetError):
        _ = Tree.from_vm(incorrect)
