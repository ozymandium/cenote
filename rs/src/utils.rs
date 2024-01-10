/// Utility functions

/// Linear interpolation
///
/// # Arguments
/// * `xs` - The x values of the data points
/// * `ys` - The y values of the data points
/// * `x` - The x value to interpolate
///
/// # Returns
/// The interpolated y value
///
/// # Errors
/// * Vectors must be of the same length
/// * Vectors must have at least two elements
/// * x is out of the range of xs
pub fn interpolate(xs: &[f64], ys: &[f64], x: f64) -> Result<f64, &'static str> {
    if xs.len() != ys.len() {
        return Err("utils::interpolate: Vectors must be of the same length");
    }
    if xs.len() < 2 {
        return Err("utils::interpolate: Vectors must have at least two elements");
    }
    for i in 0..xs.len() - 1 {
        if xs[i] <= x && x <= xs[i + 1] {
            // Perform the linear interpolation
            let slope = (ys[i + 1] - ys[i]) / (xs[i + 1] - xs[i]);
            return Ok(ys[i] + slope * (x - xs[i]));
        }
    }
    Err("utils::interpolate: x is out of the range of xs")
}

#[test]
fn test_interpolate() {
    let xs = vec![0.0, 1.0, 2.0, 3.0];
    let ys = vec![0.0, 1.0, 4.0, 9.0];
    let empty: Vec<f64> = vec![];
    let one = vec![0.0];

    assert_eq!(
        interpolate(&xs, &ys, -1.0),
        Err("utils::interpolate: x is out of the range of xs")
    );
    assert_eq!(interpolate(&xs, &ys, 0.0), Ok(0.0));
    assert_eq!(interpolate(&xs, &ys, 0.5), Ok(0.5));
    assert_eq!(interpolate(&xs, &ys, 1.0), Ok(1.0));
    assert_eq!(interpolate(&xs, &ys, 1.5), Ok(2.5));
    assert_eq!(interpolate(&xs, &ys, 2.0), Ok(4.0));
    assert_eq!(interpolate(&xs, &ys, 2.5), Ok(6.5));
    assert_eq!(interpolate(&xs, &ys, 3.0), Ok(9.0));
    assert_eq!(
        interpolate(&xs, &ys, 4.0),
        Err("utils::interpolate: x is out of the range of xs")
    );
    assert_eq!(
        interpolate(&empty, &empty, 0.0),
        Err("utils::interpolate: Vectors must have at least two elements")
    );
    assert_eq!(
        interpolate(&one, &one, 0.0),
        Err("utils::interpolate: Vectors must have at least two elements")
    );
}
