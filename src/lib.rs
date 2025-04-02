use fidget::context::{Context, Tree};
use fidget::mesh::{Mesh, Settings};
use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;

struct PyFidgetError(fidget::Error);

impl From<PyFidgetError> for PyErr {
    fn from(error: PyFidgetError) -> Self {
        PyRuntimeError::new_err(error.0.to_string())
    }
}

impl From<fidget::Error> for PyFidgetError {
    fn from(other: fidget::Error) -> Self {
        Self(other)
    }
}

#[derive(Clone)]
#[pyclass(name = "Tree")]
struct PyTree {
    _val: Tree,
}

#[pyclass(name = "Mesh")]
struct PyMesh {
    _val: Mesh,
}

#[pymethods]
impl PyMesh {
    #[getter]
    fn triangles(&self) -> Vec<(usize, usize, usize)> {
        let tri_iter = self._val.triangles.iter();
        let mut vec = std::vec::Vec::new();
        for tri in tri_iter {
            vec.push((tri.x, tri.y, tri.z));
        }
        vec
    }
    #[getter]
    fn vertices(&self) -> Vec<(f32, f32, f32)> {
        let e_iter = self._val.vertices.iter();
        let mut vec = std::vec::Vec::new();
        for e in e_iter {
            vec.push((e.x, e.y, e.z));
        }
        vec
    }
    fn to_stl(&self) -> Vec<u8> {
        let mut out = std::vec::Vec::new();
        const HEADER: &[u8] = b"This is a binary STL file exported by Fidget";
        out.extend(HEADER);
        // static_assertions::const_assert!(HEADER.len() <= 80);
        out.extend([0u8; 80 - HEADER.len()]);
        out.extend((self._val.triangles.len() as u32).to_le_bytes());
        for t in &self._val.triangles {
            // Not the _best_ way to calculate a normal, but good enough
            let a = self._val.vertices[t.x];
            let b = self._val.vertices[t.y];
            let c = self._val.vertices[t.z];
            let ab = b - a;
            let ac = c - a;
            let normal = ab.cross(&ac);
            for p in &normal {
                out.extend(p.to_le_bytes());
            }
            for v in t {
                for p in &self._val.vertices[*v] {
                    out.extend(p.to_le_bytes());
                }
            }
            out.extend([0u8; std::mem::size_of::<u16>()]); // attributes
        }
        out
    }
}

#[pymethods]
impl PyTree {
    // print to graphviz for debugging
    fn to_graphviz(&self) -> String {
        let mut ctx = Context::new();
        ctx.import(&self._val);
        ctx.dot()
    }
    fn mesh(&self, this_depth: u8) -> Result<PyMesh, PyFidgetError> {
        let mut ctx = Context::new();
        let root = ctx.import(&self._val);
        let shape = fidget::jit::JitShape::new(&ctx, root)?;
        let settings = Settings {
            depth: this_depth,
            ..Default::default()
        };
        let octree = fidget::mesh::Octree::build(&shape, settings);
        let mesh = octree.walk_dual(settings);
        Ok(PyMesh { _val: mesh })
    }
    fn __repr__(&self) -> String {
        let mut ctx = Context::new();
        ctx.import(&self._val);
        let thislen: String = ctx.len().to_string();
        format!("<Tree, {thislen} nodes>")
    }
    fn __len__(&self) -> usize {
        let mut ctx = Context::new();
        ctx.import(&self._val);
        ctx.len()
    }
    fn remap_xyz(&self, new_x: &PyTree, new_y: &PyTree, new_z: &PyTree) -> Self {
        PyTree {
            _val: self._val.to_owned().remap_xyz(
                new_x._val.to_owned(),
                new_y._val.to_owned(),
                new_z._val.to_owned(),
            ),
        }
    }
    // axis words and constants
    #[staticmethod]
    fn x() -> Self {
        PyTree { _val: Tree::x() }
    }
    #[staticmethod]
    fn y() -> Self {
        PyTree { _val: Tree::y() }
    }
    #[staticmethod]
    fn z() -> Self {
        PyTree { _val: Tree::z() }
    }
    #[staticmethod]
    fn constant(f: f64) -> Self {
        PyTree {
            _val: Tree::constant(f),
        }
    }
    // unary operations
    fn square(&self) -> Self {
        PyTree {
            _val: Tree::square(&self._val),
        }
    }
    fn floor(&self) -> Self {
        PyTree {
            _val: Tree::floor(&self._val),
        }
    }
    fn recip(&self) -> Self {
        PyTree {
            _val: Tree::constant(1.0) / self._val.to_owned(),
        }
    }
    fn ceil(&self) -> Self {
        PyTree {
            _val: Tree::ceil(&self._val),
        }
    }
    fn round(&self) -> Self {
        PyTree {
            _val: Tree::round(&self._val),
        }
    }
    fn sqrt(&self) -> Self {
        PyTree {
            _val: Tree::sqrt(&self._val),
        }
    }
    fn neg(&self) -> Self {
        PyTree {
            _val: Tree::neg(&self._val),
        }
    }
    fn sin(&self) -> Self {
        PyTree {
            _val: Tree::sin(&self._val),
        }
    }
    fn cos(&self) -> Self {
        PyTree {
            _val: Tree::cos(&self._val),
        }
    }
    fn tan(&self) -> Self {
        PyTree {
            _val: Tree::tan(&self._val),
        }
    }
    fn asin(&self) -> Self {
        PyTree {
            _val: Tree::asin(&self._val),
        }
    }
    fn acos(&self) -> Self {
        PyTree {
            _val: Tree::acos(&self._val),
        }
    }
    fn atan(&self) -> Self {
        PyTree {
            _val: Tree::atan(&self._val),
        }
    }
    fn exp(&self) -> Self {
        PyTree {
            _val: Tree::exp(&self._val),
        }
    }
    fn ln(&self) -> Self {
        PyTree {
            _val: Tree::ln(&self._val),
        }
    }
    fn not(&self) -> Self {
        PyTree {
            _val: Tree::not(&self._val),
        }
    }
    fn abs(&self) -> Self {
        PyTree {
            _val: Tree::abs(&self._val),
        }
    }
    // binary operations
    fn pow<'py>(&self, other: &Bound<'py, PyAny>) ->PyResult<Self> {
        // https://en.wikipedia.org/wiki/Exponentiation_by_squaring
        let mut n: i64 = other.extract()?;
        let mut res = self._val.to_owned();
        let mut y: Tree = Tree::constant(1.0);
        let mut first_y_mul = false;
        if n < 0 {
            n = -n;
            res = Tree::constant(1.0) / res;
        }
        else if n == 0 {
            return Ok(PyTree { _val: Tree::constant(1.0)});
        }
        while n > 1 {
            if n % 2 == 1 {
                if first_y_mul {
                    y = res.clone() * y;
                } else  {
                    y = res.clone();
                    first_y_mul = true;
                }
                n = n - 1;
            }
            res = res.clone().square();
            n = n / 2;
        }
        if first_y_mul {
            Ok(PyTree { _val: res * y })
        } else {
            Ok(PyTree { _val: res })
        }
    }
    fn add<'py>(&self, other: &Bound<'py, PyAny>) -> PyResult<Self> {
        if other.is_instance_of::<PyTree>() {
            let other = PyTree::extract_bound(other)?;
            Ok(PyTree {
                _val: self._val.to_owned() + other._val.to_owned(),
            })
        } else {
            let value: f64 = other.extract()?;
            Ok(PyTree {
                _val: self._val.to_owned() + Tree::constant(value),
            })
        }
    }
    fn sub<'py>(&self, other: &Bound<'py, PyAny>) -> PyResult<Self> {
        if other.is_instance_of::<PyTree>() {
            let other = PyTree::extract_bound(other)?;
            Ok(PyTree {
                _val: self._val.to_owned() - other._val.to_owned(),
            })
        } else {
            let value: f64 = other.extract()?;
            Ok(PyTree {
                _val: self._val.to_owned() - Tree::constant(value),
            })
        }
    }
    fn mul<'py>(&self, other: &Bound<'py, PyAny>) -> PyResult<Self> {
        if other.is_instance_of::<PyTree>() {
            let other = PyTree::extract_bound(other)?;
            Ok(PyTree {
                _val: self._val.to_owned() * other._val.to_owned(),
            })
        } else {
            let value: f64 = other.extract()?;
            Ok(PyTree {
                _val: self._val.to_owned() * Tree::constant(value),
            })
        }
    }
    fn div<'py>(&self, other: &Bound<'py, PyAny>) -> PyResult<Self> {
        if other.is_instance_of::<PyTree>() {
            let other = PyTree::extract_bound(other)?;
            Ok(PyTree {
                _val: self._val.to_owned() / other._val.to_owned(),
            })
        } else {
            let value: f64 = other.extract()?;
            Ok(PyTree {
                _val: self._val.to_owned() / Tree::constant(value),
            })
        }
    }
    fn max<'py>(&self, other: &Bound<'py, PyAny>) -> PyResult<Self> {
        if other.is_instance_of::<PyTree>() {
            let other = PyTree::extract_bound(other)?;
            Ok(PyTree {
                _val: self._val.to_owned().max(other._val.to_owned()),
            })
        } else {
            let value: f64 = other.extract()?;
            Ok(PyTree {
                _val: self._val.to_owned().max(Tree::constant(value)),
            })
        }
    }
    fn min<'py>(&self, other: &Bound<'py, PyAny>) -> PyResult<Self> {
        if other.is_instance_of::<PyTree>() {
            let other = PyTree::extract_bound(other)?;
            Ok(PyTree {
                _val: self._val.to_owned().min(other._val.to_owned()),
            })
        } else {
            let value: f64 = other.extract()?;
            Ok(PyTree {
                _val: self._val.to_owned().min(Tree::constant(value)),
            })
        }
    }
    fn compare<'py>(&self, other: &Bound<'py, PyAny>) -> PyResult<Self> {
        if other.is_instance_of::<PyTree>() {
            let other = PyTree::extract_bound(other)?;
            Ok(PyTree {
                _val: self._val.to_owned().compare(other._val.to_owned()),
            })
        } else {
            let value: f64 = other.extract()?;
            Ok(PyTree {
                _val: self._val.to_owned().compare(Tree::constant(value)),
            })
        }
    }
    fn modulo<'py>(&self, other: &Bound<'py, PyAny>) -> PyResult<Self> {
        if other.is_instance_of::<PyTree>() {
            let other = PyTree::extract_bound(other)?;
            Ok(PyTree {
                _val: self._val.to_owned().modulo(other._val.to_owned()),
            })
        } else {
            let value: f64 = other.extract()?;
            Ok(PyTree {
                _val: self._val.to_owned().modulo(Tree::constant(value)),
            })
        }
    }
    fn and<'py>(&self, other: &Bound<'py, PyAny>) -> PyResult<Self> {
        if other.is_instance_of::<PyTree>() {
            let other = PyTree::extract_bound(other)?;
            Ok(PyTree {
                _val: self._val.to_owned().and(other._val.to_owned()),
            })
        } else {
            let value: f64 = other.extract()?;
            Ok(PyTree {
                _val: self._val.to_owned().and(Tree::constant(value)),
            })
        }
    }
    fn or<'py>(&self, other: &Bound<'py, PyAny>) -> PyResult<Self> {
        if other.is_instance_of::<PyTree>() {
            let other = PyTree::extract_bound(other)?;
            Ok(PyTree {
                _val: self._val.to_owned().or(other._val.to_owned()),
            })
        } else {
            let value: f64 = other.extract()?;
            Ok(PyTree {
                _val: self._val.to_owned().or(Tree::constant(value)),
            })
        }
    }
    fn atan2<'py>(&self, other: &Bound<'py, PyAny>) -> PyResult<Self> {
        if other.is_instance_of::<PyTree>() {
            let other = PyTree::extract_bound(other)?;
            Ok(PyTree {
                _val: self._val.to_owned().atan2(other._val.to_owned()),
            })
        } else {
            let value: f64 = other.extract()?;
            Ok(PyTree {
                _val: self._val.to_owned().atan2(Tree::constant(value)),
            })
        }
    }
    // dunder method aliases
    fn __round__(&self) -> Self {
        PyTree::round(self)
    }
    fn __neg__(&self) -> Self {
        PyTree::neg(self)
    }
    fn __invert__(&self) -> Self {
        PyTree::neg(self)
    }
    fn __or__<'py>(&self, other: &Bound<'py, PyAny>) -> PyResult<Self> {
        PyTree::or(&self, &other)
    }
    fn __and__<'py>(&self, other: &Bound<'py, PyAny>) -> PyResult<Self> {
        PyTree::and(&self, &other)
    }
    fn __abs__(&self) -> Self {
        PyTree::abs(self)
    }
    fn __add__<'py>(&self, other: &Bound<'py, PyAny>) -> PyResult<Self> {
        PyTree::add(&self, &other)
    }
    fn __radd__<'py>(&self, other: &Bound<'py, PyAny>) -> PyResult<Self> {
        PyTree::add(&self, &other)
    }
    fn __sub__<'py>(&self, other: &Bound<'py, PyAny>) -> PyResult<Self> {
        PyTree::sub(&self, &other)
    }
    fn __rsub__<'py>(&self, other: &Bound<'py, PyAny>) -> PyResult<Self> {
        if other.is_instance_of::<PyTree>() {
            let other = PyTree::extract_bound(other)?;
            Ok(PyTree {
                _val: other._val.to_owned() - self._val.to_owned(),
            })
        } else {
            let value: f64 = other.extract()?;
            Ok(PyTree {
                _val: Tree::constant(value) - self._val.to_owned(),
            })
        }
    }
    fn __mul__<'py>(&self, other: &Bound<'py, PyAny>) -> PyResult<Self> {
        PyTree::mul(&self, &other)
    }
    fn __rmul__<'py>(&self, other: &Bound<'py, PyAny>) -> PyResult<Self> {
        PyTree::mul(&self, &other)
    }
    fn __truediv__<'py>(&self, other: &Bound<'py, PyAny>) -> PyResult<Self> {
        PyTree::div(&self, &other)
    }
    fn __rtruediv__<'py>(&self, other: &Bound<'py, PyAny>) -> PyResult<Self> {
        if other.is_instance_of::<PyTree>() {
            let other = PyTree::extract_bound(other)?;
            Ok(PyTree {
                _val: other._val.to_owned() / self._val.to_owned(),
            })
        } else {
            let value: f64 = other.extract()?;
            Ok(PyTree {
                _val: Tree::constant(value) / self._val.to_owned(),
            })
        }
    }
    fn __mod__<'py>(&self, other: &Bound<'py, PyAny>) -> PyResult<Self> {
        PyTree::modulo(&self, &other)
    }
    fn __rmod__<'py>(&self, other: &Bound<'py, PyAny>) -> PyResult<Self> {
        if other.is_instance_of::<PyTree>() {
            let other = PyTree::extract_bound(other)?;
            Ok(PyTree {
                _val: other._val.to_owned().modulo(self._val.to_owned()),
            })
        } else {
            let value: f64 = other.extract()?;
            Ok(PyTree {
                _val: Tree::constant(value).modulo(self._val.to_owned()),
            })
        }
    }
    fn __pow__<'py>(&self, other: &Bound<'py, PyAny>, modval: Option<&Bound<'py, PyAny>>) -> PyResult<Self> {
        match modval {
        Some(_) => Err(PyRuntimeError::new_err("mod option not available for Tree")),
        None => Ok(PyTree::pow(&self, &other)?)
        }
    }
}

/// A Python module implemented in Rust. The name of this function must match
/// the `lib.name` setting in the `Cargo.toml`, else Python will not be able to
/// import the module.
#[pymodule]
fn _core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyTree>()?;
    m.add_class::<PyMesh>()?;
    Ok(())
}
