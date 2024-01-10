use crate::units::{bar, min, Bar, Min, Pressure, Time};

#[derive(Debug)]
struct Params {
    half_life: Time,
    /// Coefficient `a` is the y-intercept of the M-value line
    a: Pressure,
    /// Coefficient `b` is the reciprocal of the slope of the M-value line
    b: f64,
}

impl Params {
    fn new(half_life: Time) -> Result<Self, &'static str> {
        if half_life.get::<Min>() <= 0.0 {
            return Err("deco::buhlmann::compartment::Params::new: half_life must be positive");
        }
        let cbrt_t_min: f64 = half_life.get::<Min>().cbrt();
        let sqrt_t_min: f64 = half_life.get::<Min>().sqrt();
        Ok(Params {
            half_life: half_life,
            a: bar(2.0 / cbrt_t_min),
            b: 1.005 - 1.0 / sqrt_t_min,
        })
    }
}

#[test]
fn test_params_new_valid() {
    use crate::assert_approx_val;
    let params = Params::new(min(3.0)).unwrap();
    assert_eq!(params.half_life.get::<Min>(), 3.0);
    assert_approx_val!(params.a.get::<Bar>(), 1.3867225487012695, 1e-15);
    assert_approx_val!(params.b, 0.42764973081037405, 1e-15);
}

#[test]
fn test_params_new_invalid() {
    assert_eq!(
        Params::new(min(0.0)).unwrap_err(),
        "deco::buhlmann::compartment::Params::new: half_life must be positive"
    );
}
