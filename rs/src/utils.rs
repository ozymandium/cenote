

// Linear interpolation
//
// # Arguments
// * `xs` - The x values of the data points
// * `ys` - The y values of the data points
// * `x` - The x value to interpolate
//
// # Returns
// * `Some(f64)` - The interpolated y value
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
