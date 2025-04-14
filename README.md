# FidgetPy

Python bindings and high-level API for [Fidget](https://github.com/mkeeter/fidget).

## Usage

``` python
import fidgetpy as fp

# create a torus
p = fp.axes()
q = fp.Vec2(p.xy.length() - 0.6, p.z)
torus = q.length() - 0.15
# convert to a triangle mesh
mesh = torus.mesh(5)
print(f"torus mesh has {len(mesh.vertices)} vertices and {len(mesh.triangles)} faces")
# write to an stl file
with open("./torus.stl", "wb") as f:
    f.write(mesh.to_stl())

```

Refer to the [examples](examples/README.md) folder for additonal usage details.
