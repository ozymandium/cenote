// Linear interpolation
//
// # Arguments
// * `xs` - The x values of the data points
// * `ys` - The y values of the data points
// * `x` - The x value to interpolate
//
// # Returns
// * `Some(f64)` - The interpolated y value if the x value is in the range of xs
// * `None` - The x value is out of the range of xs
pub fn interpolate(xs: &[f64], ys: &[f64], x: f64) -> Option<f64> {
    if xs.len() != ys.len() || xs.is_empty() {
        return None; // Vectors must be of the same non-zero length
    }

    for i in 0..xs.len() - 1 {
        if xs[i] <= x && x <= xs[i + 1] {
            // Perform the linear interpolation
            let slope = (ys[i + 1] - ys[i]) / (xs[i + 1] - xs[i]);
            return Some(ys[i] + slope * (x - xs[i]));
        }
    }

    None // x is out of the range of xs
}

#[test]
fn test_interpolate() {
    let xs = vec![0.0, 1.0, 2.0, 3.0];
    let ys = vec![0.0, 1.0, 4.0, 9.0];

    assert_eq!(interpolate(&xs, &ys, -1.0), None);
    assert_eq!(interpolate(&xs, &ys, 0.0), Some(0.0));
    assert_eq!(interpolate(&xs, &ys, 0.5), Some(0.5));
    assert_eq!(interpolate(&xs, &ys, 1.0), Some(1.0));
    assert_eq!(interpolate(&xs, &ys, 1.5), Some(2.5));
    assert_eq!(interpolate(&xs, &ys, 2.0), Some(4.0));
    assert_eq!(interpolate(&xs, &ys, 2.5), Some(6.5));
    assert_eq!(interpolate(&xs, &ys, 3.0), Some(9.0));
    assert_eq!(interpolate(&xs, &ys, 4.0), None);
}
