use dimensioned::Abs;
use dimensioned::Dimensioned;
use std::fmt::Debug;
use std::ops::Sub;

pub fn assert_approx<T>(lhs: &T, rhs: &T, tol: &T)
where
    T: Dimensioned + Sub<Output = T> + Abs + PartialOrd + Debug + Copy,
{
    let diff = (*lhs - *rhs).abs();
    assert!(
        diff <= *tol,
        "assertion failed: `(left ≈ right)`\n  left: `{:?}`,\n right: `{:?}`",
        lhs,
        rhs
    );
}
