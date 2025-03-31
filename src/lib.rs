use fidget::context::{Context, Tree};
use pyo3::prelude::*;


#[pyclass]
struct PyTree {
    _val: Tree,
}

impl<'py> FromPyObject<'py> for PyTree {
    // convert python ints and floats to PyTrees implicitly
    fn extract_bound(obj: &Bound<'py, PyAny>) -> PyResult<Self> {
        if obj.is_instance_of::<PyTree>() {
           //Ok(obj.unbind().)
            Ok(PyTree {
            _val: Tree::constant(5.0),
        })
        }
        else {let value: f64 = obj.extract()?;
        Ok(PyTree {
            _val: Tree::constant(value),
        })}
    }
}

// fn implicit_cast(obj: &PyAny) -> PyResult<PyTree> {
//     if PyAny::is_type_of_bound()
//     let val: f64 = obj.into()
//     let value: f64 = obj.extract()?;
//         Ok(PyTree {
//             _val: Tree::constant(value),
//         })
// }


#[derive(Clone)]
#[pyclass]
struct Foo(i64);

#[pyclass]
struct IntoFoo(Foo);

impl Into<Foo> for IntoFoo {
    fn into(self) -> Foo {
        self.0
    }

}

// If I remove this it compiles, but calling in Python: `>>> recive_from_int(42)`
// causes this error: `TypeError: argument 'foo': 'int' object cannot be converted to 'Foo'`
impl<'py> FromPyObject<'py> for IntoFoo {

    fn extract_bound(obj: &Bound<'py, PyAny>) -> PyResult<Self> {
        let value: Foo = obj.extract()?;
        Ok(IntoFoo(value))
    }
}


#[pymethods]
impl Foo {
    #[new]
    fn new(v: i64) -> Self {
        Foo(v)
    }
    #[staticmethod]
    fn receive_foo_from_int(foo: Foo) -> PyResult<i64> {
        Ok(foo.0)
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
    fn myadd<'py>(&self, other: &Bound<'py, PyAny>) -> PyResult<PyTree> {
        let extracted= PyTree::extract_bound(other)?;
        Ok(PyTree { _val: self._val.to_owned() + extracted._val.to_owned()})
    }
    fn add(&self, other: &PyTree) -> Self {
        PyTree {
            _val: self._val.to_owned() + other._val.to_owned(),
        }
    }
    fn sub(&self, other: &PyTree) -> Self {
        PyTree {
            _val: self._val.to_owned() - other._val.to_owned(),
        }
    }
    fn mul(&self, other: &PyTree) -> Self {
        PyTree {
            _val: self._val.to_owned() * other._val.to_owned(),
        }
    }
    fn div(&self, other: &PyTree) -> Self {
        PyTree {
            _val: self._val.to_owned() / other._val.to_owned(),
        }
    }

    fn max(&self, other: &PyTree) -> Self {
        PyTree {
            _val: self._val.to_owned().max(other._val.to_owned()),
        }
    }
    fn min(&self, other: &PyTree) -> Self {
        PyTree {
            _val: self._val.to_owned().min(other._val.to_owned()),
        }
    }
    fn compare(&self, other: &PyTree) -> Self {
        PyTree {
            _val: self._val.to_owned().compare(other._val.to_owned()),
        }
    }
    fn modulo(&self, other: &PyTree) -> Self {
        PyTree {
            _val: self._val.to_owned().modulo(other._val.to_owned()),
        }
    }
    fn and(&self, other: &PyTree) -> Self {
        PyTree {
            _val: self._val.to_owned().and(other._val.to_owned()),
        }
    }
    fn or(&self, other: &PyTree) -> Self {
        PyTree {
            _val: self._val.to_owned().or(other._val.to_owned()),
        }
    }
    fn atan2(&self, other: &PyTree) -> Self {
        PyTree {
            _val: self._val.to_owned().atan2(other._val.to_owned()),
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
    fn __or__(&self, other: &PyTree) -> Self {
        // boolean union
        PyTree::min(&self, &other)
    }
    fn __and__(&self, other: &PyTree) -> Self {
        // boolean intersection
        PyTree::max(&self, &other)
    }
    fn __abs__(&self) -> Self {
        PyTree::abs(self)
    }
    fn __add__(&self, other: &PyTree) -> Self {
        PyTree::add(&self, &other)
    }
    fn __radd__(&self, other: &PyTree) -> Self {
        PyTree::add(&other, &self)
    }
    fn __sub__(&self, other: &PyTree) -> Self {
        PyTree::sub(&self, &other)
    }
    fn __rsub__(&self, other: &PyTree) -> Self {
        PyTree::sub(&other, &self)
    }
    fn __mul__(&self, other: &PyTree) -> Self {
        PyTree::mul(&self, &other)
    }
    fn __rmul__(&self, other: &PyTree) -> Self {
        PyTree::mul(&other, &self)
    }
    fn __truediv__(&self, other: &PyTree) -> Self {
        PyTree::div(&self, &other)
    }
    fn __rtruediv__(&self, other: &PyTree) -> Self {
        PyTree::div(&other, &self)
    }
    fn __mod__(&self, other: &PyTree) -> Self {
        PyTree::modulo(&self, &other)
    }
    fn __rmod__(&self, other: &PyTree) -> Self {
        PyTree::modulo(&other, &self)
    }
}

/// A Python module implemented in Rust. The name of this function must match
/// the `lib.name` setting in the `Cargo.toml`, else Python will not be able to
/// import the module.
#[pymodule]
fn _core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // m.add_function(wrap_pyfunction!(receive_foo_from_int, m)?)?;
    m.add_class::<Foo>()?;
    m.add_class::<PyTree>()?;
    Ok(())
}
