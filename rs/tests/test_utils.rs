// Unit tests for the utils module.

extern crate cenote;

use cenote::utils;

#[test]
fn test_interpolate() {
    let xs = vec![0.0, 1.0, 2.0, 3.0];
    let ys = vec![0.0, 1.0, 4.0, 9.0];

    assert_eq!(utils::interpolate(&xs, &ys, -1.0), None);
    assert_eq!(utils::interpolate(&xs, &ys, 0.0), Some(0.0));
    assert_eq!(utils::interpolate(&xs, &ys, 0.5), Some(0.5));
    assert_eq!(utils::interpolate(&xs, &ys, 1.0), Some(1.0));
    assert_eq!(utils::interpolate(&xs, &ys, 1.5), Some(2.5));
    assert_eq!(utils::interpolate(&xs, &ys, 2.0), Some(4.0));
    assert_eq!(utils::interpolate(&xs, &ys, 2.5), Some(6.5));
    assert_eq!(utils::interpolate(&xs, &ys, 3.0), Some(9.0));
    assert_eq!(utils::interpolate(&xs, &ys, 4.0), None);
}
