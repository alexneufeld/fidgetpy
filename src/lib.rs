use pyo3::prelude::*;
// use fidget::{context::Context, Error, context::Node, context::Op, context::UnaryOpcode};
// use fidget::context::UnaryOpcode;
// use fidget::context::BinaryOpcode;
use fidget::context::Tree;
// use pyo3::exceptions::PyValueError;
use pyo3::PyResult;


#[pyclass]
struct PyTree {
    _val: Tree
}

#[pymethods]
impl PyTree {
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
}

// #[pyclass]
// struct PyUnaryOpcode {
//     optype: UnaryOpcode
// }
//
// #[pymethods]
// impl PyUnaryOpcode {
//     #[new]
//     fn new(value: &str) -> PyResult<Self> {
//         match value {
//             "abs" => Ok(PyUnaryOpcode {optype: UnaryOpcode::Abs}),
//             "acos" => Ok(PyUnaryOpcode {optype: UnaryOpcode::Acos}),
//             "asin" => Ok(PyUnaryOpcode {optype: UnaryOpcode::Asin}),
//             "atan" => Ok(PyUnaryOpcode {optype: UnaryOpcode::Atan}),
//             "ceil" => Ok(PyUnaryOpcode {optype: UnaryOpcode::Ceil}),
//             "cos" => Ok(PyUnaryOpcode {optype: UnaryOpcode::Cos}),
//             "exp" => Ok(PyUnaryOpcode {optype: UnaryOpcode::Exp}),
//             "floor" => Ok(PyUnaryOpcode {optype: UnaryOpcode::Floor}),
//             "ln" => Ok(PyUnaryOpcode {optype: UnaryOpcode::Ln}),
//             "neg" => Ok(PyUnaryOpcode {optype: UnaryOpcode::Neg}),
//             "not" => Ok(PyUnaryOpcode {optype: UnaryOpcode::Not}),
//             "recip" => Ok(PyUnaryOpcode {optype: UnaryOpcode::Recip}),
//             "round" => Ok(PyUnaryOpcode {optype: UnaryOpcode::Round}),
//             "sin" => Ok(PyUnaryOpcode {optype: UnaryOpcode::Sin}),
//             "sqrt" => Ok(PyUnaryOpcode {optype: UnaryOpcode::Sqrt}),
//             "square" => Ok(PyUnaryOpcode {optype: UnaryOpcode::Square}),
//             "tan" => Ok(PyUnaryOpcode {optype: UnaryOpcode::Tan}),
//             _ => Err(PyValueError::new_err("invalid opcode name"))
//         }
//     }
// }
//
//
//
//
// #[pyclass]
// struct PyBinaryOpcode {
//     optype: BinaryOpcode
// }
//
// #[pymethods]
// impl PyBinaryOpcode {
//     #[new]
//     fn new(value: &str) -> PyResult<Self> {
//         match value {
//             "add" => Ok(PyBinaryOpcode {optype: BinaryOpcode::Add}),
//             "and" => Ok(PyBinaryOpcode {optype: BinaryOpcode::And}),
//             "atan2" => Ok(PyBinaryOpcode {optype: BinaryOpcode::Atan}),
//             "compare" => Ok(PyBinaryOpcode {optype: BinaryOpcode::Compare}),
//             "div" => Ok(PyBinaryOpcode {optype: BinaryOpcode::Div}),
//             "max" => Ok(PyBinaryOpcode {optype: BinaryOpcode::Max}),
//             "min" => Ok(PyBinaryOpcode {optype: BinaryOpcode::Min}),
//             "mod" => Ok(PyBinaryOpcode {optype: BinaryOpcode::Mod}),
//             "or" => Ok(PyBinaryOpcode {optype: BinaryOpcode::Or}),
//             "sub" => Ok(PyBinaryOpcode {optype: BinaryOpcode::Sub}),
//             _ => Err(PyValueError::new_err("invalid opcode name"))
//         }
//     }
// }

// #[pyfunction]
// fn hello_from_bin() -> String {
//     "Hello from fidgetpy!".to_string()
// }


// #[pyfunction]
// fn fidget_hello() -> Node {
//     let mut ctx = Context::new();
//     let x = ctx.x();
//     let y = ctx.y();
//     return ctx.add(x, y).expect("fail")
// }

/// A Python module implemented in Rust. The name of this function must match
/// the `lib.name` setting in the `Cargo.toml`, else Python will not be able to
/// import the module.
#[pymodule]
fn _core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // m.add_function(wrap_pyfunction!(hello_from_bin, m)?)?;
    m.add_class::<PyTree>()?;
    //m.add_class::<PyBinaryOpcode>()?;
    Ok(())
}
