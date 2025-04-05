use fidget::{
    compiler::{SsaOp, SsaTape},
    context::{Context, Tree},
    mesh::{Mesh, Settings},
};
use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use std::{cmp::Ordering, collections::HashMap};

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
    #[staticmethod]
    fn from_vm(src: &str) -> Result<Self, PyFidgetError> {
        let (ctx, root) = Context::from_text(src.as_bytes())?;
        Ok(PyTree {
            _val: ctx.export(root)?,
        })
    }
    fn to_vm(&self) -> Result<String, PyFidgetError> {
        let mut ctx = Context::new();
        let root = ctx.import(&self._val);
        let (ssatape, _) = SsaTape::new(&ctx, &[root])?;
        let mut result = String::new();
        let mut addr: u32 = 0;
        let mut regmap = HashMap::<u32, u32>::new();
        let mut constmap = HashMap::<[u8; 4], u32>::new();
        for &op in ssatape.tape.iter().rev() {
            match op {
                SsaOp::Output(..) => {}
                SsaOp::Input(out, i) => {
                    let varname = match i {
                        0 => "var-x",
                        1 => "var-y",
                        2 => "var-z",
                        _ => unreachable!(),
                    };
                    result.push_str(&format!("${addr} {varname}\n"));
                    regmap.insert(out, addr);
                    addr += 1;
                }
                SsaOp::NegReg(out, arg)
                | SsaOp::AbsReg(out, arg)
                | SsaOp::RecipReg(out, arg)
                | SsaOp::SqrtReg(out, arg)
                | SsaOp::CopyReg(out, arg)
                | SsaOp::SquareReg(out, arg)
                | SsaOp::FloorReg(out, arg)
                | SsaOp::CeilReg(out, arg)
                | SsaOp::RoundReg(out, arg)
                | SsaOp::SinReg(out, arg)
                | SsaOp::CosReg(out, arg)
                | SsaOp::TanReg(out, arg)
                | SsaOp::AsinReg(out, arg)
                | SsaOp::AcosReg(out, arg)
                | SsaOp::AtanReg(out, arg)
                | SsaOp::ExpReg(out, arg)
                | SsaOp::LnReg(out, arg)
                | SsaOp::NotReg(out, arg) => {
                    let op = match op {
                        SsaOp::NegReg(..) => "neg",
                        SsaOp::AbsReg(..) => "abs",
                        SsaOp::RecipReg(..) => "recip",
                        SsaOp::SqrtReg(..) => "sqrt",
                        SsaOp::SquareReg(..) => "square",
                        SsaOp::FloorReg(..) => "floor",
                        SsaOp::CeilReg(..) => "ceil",
                        SsaOp::RoundReg(..) => "round",
                        SsaOp::SinReg(..) => "sin",
                        SsaOp::CosReg(..) => "cos",
                        SsaOp::TanReg(..) => "tan",
                        SsaOp::AsinReg(..) => "asin",
                        SsaOp::AcosReg(..) => "acos",
                        SsaOp::AtanReg(..) => "atan",
                        SsaOp::ExpReg(..) => "exp",
                        SsaOp::LnReg(..) => "ln",
                        SsaOp::NotReg(..) => "not",
                        SsaOp::CopyReg(..) => "copy",
                        _ => unreachable!(),
                    };
                    let arg_addr = match regmap.get(&arg) {
                        Some(x) => x,
                        None => unreachable!(),
                    };
                    result.push_str(&format!("${addr} {op} ${arg_addr}\n"));
                    regmap.insert(out, addr);
                    addr += 1;
                }

                SsaOp::AddRegReg(out, lhs, rhs)
                | SsaOp::MulRegReg(out, lhs, rhs)
                | SsaOp::DivRegReg(out, lhs, rhs)
                | SsaOp::SubRegReg(out, lhs, rhs)
                | SsaOp::MinRegReg(out, lhs, rhs)
                | SsaOp::MaxRegReg(out, lhs, rhs)
                | SsaOp::ModRegReg(out, lhs, rhs)
                | SsaOp::AndRegReg(out, lhs, rhs)
                | SsaOp::AtanRegReg(out, lhs, rhs)
                | SsaOp::OrRegReg(out, lhs, rhs) => {
                    let op = match op {
                        SsaOp::AddRegReg(..) => "add",
                        SsaOp::MulRegReg(..) => "mul",
                        SsaOp::DivRegReg(..) => "div",
                        SsaOp::AtanRegReg(..) => "atan",
                        SsaOp::SubRegReg(..) => "sub",
                        SsaOp::MinRegReg(..) => "min",
                        SsaOp::MaxRegReg(..) => "max",
                        SsaOp::ModRegReg(..) => "max",
                        SsaOp::AndRegReg(..) => "and",
                        SsaOp::OrRegReg(..) => "or",
                        _ => unreachable!(),
                    };
                    let lhs_addr = match regmap.get(&lhs) {
                        Some(x) => x,
                        None => unreachable!(),
                    };
                    let rhs_addr = match regmap.get(&rhs) {
                        Some(x) => x,
                        None => unreachable!(),
                    };
                    result.push_str(&format!("${addr} {op} ${lhs_addr} ${rhs_addr}\n"));
                    regmap.insert(out, addr);
                    addr += 1;
                }

                SsaOp::AddRegImm(out, arg, imm)
                | SsaOp::MulRegImm(out, arg, imm)
                | SsaOp::DivRegImm(out, arg, imm)
                | SsaOp::DivImmReg(out, arg, imm)
                | SsaOp::SubImmReg(out, arg, imm)
                | SsaOp::SubRegImm(out, arg, imm)
                | SsaOp::AtanRegImm(out, arg, imm)
                | SsaOp::AtanImmReg(out, arg, imm)
                | SsaOp::MinRegImm(out, arg, imm)
                | SsaOp::MaxRegImm(out, arg, imm)
                | SsaOp::ModRegImm(out, arg, imm)
                | SsaOp::ModImmReg(out, arg, imm)
                | SsaOp::AndRegImm(out, arg, imm)
                | SsaOp::OrRegImm(out, arg, imm) => {
                    let (op, swap) = match op {
                        SsaOp::AddRegImm(..) => ("add", false),
                        SsaOp::MulRegImm(..) => ("mul", false),
                        SsaOp::DivImmReg(..) => ("div", true),
                        SsaOp::DivRegImm(..) => ("div", false),
                        SsaOp::SubImmReg(..) => ("sub", true),
                        SsaOp::SubRegImm(..) => ("sub", false),
                        SsaOp::AtanImmReg(..) => ("atan", true),
                        SsaOp::AtanRegImm(..) => ("atan", false),
                        SsaOp::MinRegImm(..) => ("min", false),
                        SsaOp::MaxRegImm(..) => ("max", false),
                        SsaOp::ModRegImm(..) => ("mod", false),
                        SsaOp::ModImmReg(..) => ("mod", true),
                        SsaOp::AndRegImm(..) => ("and", false),
                        SsaOp::OrRegImm(..) => ("or", false),
                        _ => unreachable!(),
                    };
                    let imm_addr = if let std::collections::hash_map::Entry::Vacant(e) =
                        constmap.entry(imm.to_ne_bytes())
                    {
                        e.insert(addr);
                        result.push_str(&format!("${addr} const {imm}\n"));
                        addr += 1;
                        addr - 1
                    } else {
                        *match constmap.get(&imm.to_ne_bytes()) {
                            Some(x) => x,
                            None => unreachable!(),
                        }
                    };
                    let arg_addr = match regmap.get(&arg) {
                        Some(x) => x,
                        None => unreachable!(),
                    };
                    if swap {
                        result.push_str(&format!("${addr} {op} ${imm_addr} ${arg_addr}\n"));
                    } else {
                        result.push_str(&format!("${addr} {op} ${arg_addr} ${imm_addr}\n"));
                    }
                    regmap.insert(out, addr);
                    addr += 1;
                }
                SsaOp::CompareRegReg(out, lhs, rhs) => {
                    let lhs_addr = match regmap.get(&lhs) {
                        Some(x) => x,
                        None => unreachable!(),
                    };
                    let rhs_addr = match regmap.get(&rhs) {
                        Some(x) => x,
                        None => unreachable!(),
                    };
                    result.push_str(&format!("${addr} compare ${lhs_addr} ${rhs_addr}\n"));
                    regmap.insert(out, addr);
                    addr += 1;
                }
                SsaOp::CompareRegImm(out, arg, imm) => {
                    let imm_addr = if let std::collections::hash_map::Entry::Vacant(e) =
                        constmap.entry(imm.to_ne_bytes())
                    {
                        e.insert(addr);
                        result.push_str(&format!("${addr} const {imm}\n"));
                        addr += 1;
                        addr - 1
                    } else {
                        *match constmap.get(&imm.to_ne_bytes()) {
                            Some(x) => x,
                            None => unreachable!(),
                        }
                    };
                    let arg_addr = match regmap.get(&arg) {
                        Some(x) => x,
                        None => unreachable!(),
                    };
                    result.push_str(&format!("${addr} compare ${arg_addr} ${imm_addr}\n"));
                    regmap.insert(out, addr);
                    addr += 1;
                }
                SsaOp::CompareImmReg(out, arg, imm) => {
                    let imm_addr = if let std::collections::hash_map::Entry::Vacant(e) =
                        constmap.entry(imm.to_ne_bytes())
                    {
                        e.insert(addr);
                        result.push_str(&format!("${addr} const {imm}\n"));
                        addr += 1;
                        addr - 1
                    } else {
                        *match constmap.get(&imm.to_ne_bytes()) {
                            Some(x) => x,
                            None => unreachable!(),
                        }
                    };
                    let arg_addr = match regmap.get(&arg) {
                        Some(x) => x,
                        None => unreachable!(),
                    };
                    result.push_str(&format!("${addr} compare ${imm_addr} ${arg_addr}\n"));
                    regmap.insert(out, addr);
                    addr += 1;
                }
                SsaOp::CopyImm(_out, imm) => {
                    // result.push_str(&format!("${out} copy {imm}\n"));
                    if let std::collections::hash_map::Entry::Vacant(e) =
                        constmap.entry(imm.to_ne_bytes())
                    {
                        e.insert(addr);
                        result.push_str(&format!("${addr} const {imm}\n"));
                        addr += 1;
                    }
                }
            }
        }
        Ok(result)
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
    fn remap_xyz(
        &self,
        new_x: &PyTree,
        new_y: &PyTree,
        new_z: &PyTree,
    ) -> Result<Self, PyFidgetError> {
        // don't lazily evaluate remappings to prevent unexpected results due to nested remap calls
        let remapped_tree = self._val.to_owned().remap_xyz(
            new_x._val.to_owned(),
            new_y._val.to_owned(),
            new_z._val.to_owned(),
        );
        let mut ctx = Context::new();
        let root = ctx.import(&remapped_tree);
        // let root = ctx.import(&self._val);
        // root.remap_xyz();
        Ok(PyTree {
            _val: ctx.export(root)?,
        })
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
    fn pow(&self, other: &Bound<'_, PyAny>) -> PyResult<Self> {
        // https://en.wikipedia.org/wiki/Exponentiation_by_squaring
        let mut n: i64 = other.extract()?;
        let mut res = self._val.to_owned();
        let mut y: Tree = Tree::constant(1.0);
        let mut first_y_mul = false;
        match n.cmp(&0) {
            Ordering::Less => {
                n = -n;
                res = Tree::constant(1.0) / res;
            }
            Ordering::Equal => {
                return Ok(PyTree {
                    _val: Tree::constant(1.0),
                });
            }
            Ordering::Greater => {}
        }
        while n > 1 {
            if n % 2 == 1 {
                if first_y_mul {
                    y = res.clone() * y;
                } else {
                    y = res.clone();
                    first_y_mul = true;
                }
                n -= 1;
            }
            res = res.clone().square();
            n /= 2;
        }
        if first_y_mul {
            Ok(PyTree { _val: res * y })
        } else {
            Ok(PyTree { _val: res })
        }
    }
    fn add(&self, other: &Bound<'_, PyAny>) -> PyResult<Self> {
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
    fn sub(&self, other: &Bound<'_, PyAny>) -> PyResult<Self> {
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
    fn mul(&self, other: &Bound<'_, PyAny>) -> PyResult<Self> {
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
    fn div(&self, other: &Bound<'_, PyAny>) -> PyResult<Self> {
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
    fn max(&self, other: &Bound<'_, PyAny>) -> PyResult<Self> {
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
    fn min(&self, other: &Bound<'_, PyAny>) -> PyResult<Self> {
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
    fn compare(&self, other: &Bound<'_, PyAny>) -> PyResult<Self> {
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
    fn modulo(&self, other: &Bound<'_, PyAny>) -> PyResult<Self> {
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
    fn and(&self, other: &Bound<'_, PyAny>) -> PyResult<Self> {
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
    fn or(&self, other: &Bound<'_, PyAny>) -> PyResult<Self> {
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
    fn atan2(&self, other: &Bound<'_, PyAny>) -> PyResult<Self> {
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
    fn __or__(&self, other: &Bound<'_, PyAny>) -> PyResult<Self> {
        PyTree::or(self, other)
    }
    fn __and__(&self, other: &Bound<'_, PyAny>) -> PyResult<Self> {
        PyTree::and(self, other)
    }
    fn __abs__(&self) -> Self {
        PyTree::abs(self)
    }
    fn __add__(&self, other: &Bound<'_, PyAny>) -> PyResult<Self> {
        PyTree::add(self, other)
    }
    fn __radd__(&self, other: &Bound<'_, PyAny>) -> PyResult<Self> {
        PyTree::add(self, other)
    }
    fn __sub__(&self, other: &Bound<'_, PyAny>) -> PyResult<Self> {
        PyTree::sub(self, other)
    }
    fn __rsub__(&self, other: &Bound<'_, PyAny>) -> PyResult<Self> {
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
    fn __mul__(&self, other: &Bound<'_, PyAny>) -> PyResult<Self> {
        PyTree::mul(self, other)
    }
    fn __rmul__(&self, other: &Bound<'_, PyAny>) -> PyResult<Self> {
        PyTree::mul(self, other)
    }
    fn __truediv__(&self, other: &Bound<'_, PyAny>) -> PyResult<Self> {
        PyTree::div(self, other)
    }
    fn __rtruediv__(&self, other: &Bound<'_, PyAny>) -> PyResult<Self> {
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
    fn __mod__(&self, other: &Bound<'_, PyAny>) -> PyResult<Self> {
        PyTree::modulo(self, other)
    }
    fn __rmod__(&self, other: &Bound<'_, PyAny>) -> PyResult<Self> {
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
    fn __pow__<'py>(
        &self,
        other: &Bound<'py, PyAny>,
        modval: Option<&Bound<'py, PyAny>>,
    ) -> PyResult<Self> {
        match modval {
            Some(_) => Err(PyRuntimeError::new_err("mod option not available for Tree")),
            None => Ok(PyTree::pow(self, other)?),
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
