/// Macros

/// Compare two floating point numbers for approximate equality
///
/// # Arguments
/// * `lhs` - The left hand side of the comparison
/// * `rhs` - The right hand side of the comparison
/// * `tol` - The tolerance for the comparison
///
/// # Panics
/// Panics if the two values are not approximately equal
macro_rules! assert_approx {
    ($lhs:expr, $rhs:expr, $tol:expr) => {
        {
            let diff = (*$lhs - *$rhs).abs();
            assert!(
                diff <= *$tol,
                "assertion failed: `(left ≈ right)`\n  left: `{:?}`,\n  right: `{:?}`,\n  tol: `{:?}`",
                $lhs,
                $rhs,
                $tol
            );
        }
    };
}

pub(crate) use assert_approx;
