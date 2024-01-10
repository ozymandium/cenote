use crate::units::{bar, Bar, Min, Pressure, Time};

struct Params {
    half_life: Time,
    /// Coefficient `a` is the y-intercept of the M-value line
    a: Pressure,
    /// Coefficient `b` is the reciprocal of the slope of the M-value line
    b: f64,
}

impl Params {
    fn new(half_life: Time) -> Self {
        let cbrt_t_min: f64 = half_life.get::<Min>().cbrt();
        let sqrt_t_min: f64 = half_life.get::<Min>().sqrt();
        Params {
            half_life: half_life,
            a: bar(2.0 / cbrt_t_min),
            b: 1.005 - 1.0 / sqrt_t_min,
        }
    }
}
