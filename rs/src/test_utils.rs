use dimensioned::Dimensioned;
use std::ops::Sub;

// pub fn assert_approx<T>(lhs: T, rhs: T, tol: T)
// where
//     T: Dimensioned<Value = f64> + Sub<Output = T> + Into<f64>,
// {
//     // since dimensioned quantities implement each individual unit as a type, we know that all
//     // quantities are of the same type, so we can convert them to f64 without conversion
//     let lhs_val: f64 = lhs.into();
//     let rhs_val: f64 = rhs.into();
//     let tol_val: f64 = tol.into();

//     assert!((lhs_val - rhs_val).abs() <= tol_val);
// }
