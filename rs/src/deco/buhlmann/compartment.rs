#[cfg(test)]
use crate::assert_approx_val;
use crate::constants::WATER_VAPOR_PRESSURE;
#[cfg(test)]
use crate::units::min;
use crate::units::{bar, Bar, Min, Pressure, Time};

#[derive(Debug)]
pub struct Params {
    /// Half life of the compartment
    pub hl: Time,
    /// Coefficient `a` is the y-intercept of the M-value line
    pub a: Pressure,
    /// Coefficient `b` is the reciprocal of the slope of the M-value line
    pub b: f64,
}

impl Params {
    fn new(half_life: Time) -> Result<Self, &'static str> {
        if half_life.get::<Min>() <= 0.0 {
            return Err("deco::buhlmann::compartment::Params::new: half_life must be positive");
        }
        let cbrt_t_min: f64 = half_life.get::<Min>().cbrt();
        let sqrt_t_min: f64 = half_life.get::<Min>().sqrt();
        Ok(Params {
            hl: half_life,
            a: bar(2.0 / cbrt_t_min),
            b: 1.005 - 1.0 / sqrt_t_min,
        })
    }
}

/// A single tissue compartment in the Buhlmann decompression model for a single gas
#[derive(Debug)]
pub struct Compartment {
    pub params: Params,
    /// The current pressure of the compartment
    pub pressure: Pressure,
    /// The Buhlmann M0 value for the compartment. This is the lowest tolerable ambient gas pressure
    /// to which this compartment can be exposed bases on the current value of the compartment
    /// gas pressure stored in `pressure`.
    pub m0: Pressure,
}

impl Compartment {
    /// Create a new compartment with the given half life and initial pressure.
    ///
    /// # Arguments
    /// * `half_life` - The half life of the compartment
    /// * `pressure` - The initial absolute internal pressure of the compartment.
    pub fn new(half_life: Time, pressure: Pressure) -> Result<Self, &'static str> {
        let params = Params::new(half_life)?;
        let mut compartment = Compartment {
            params,
            pressure: Pressure::default(),
            m0: Pressure::default(),
        };
        compartment.set(pressure);
        Ok(compartment)
    }

    /// Update the compartment internal pressure and M0 value.
    /// Calculate the M0 value for a compartment given the compartment pressure. M0 is the lowest
    /// tolerable ambient gas pressure to which this compartment can be exposed based on the current
    /// value of the compartment gas pressure. M0 corresponds to a gradient of 1.0.
    ///
    /// M value plot has ambient pressure on x axis and compartment pressure on y axis
    /// M value forms a line with slope and y intercept forms the tolerable compartment pressure at
    /// the surface.
    ///
    /// Ptol = (Pcmp - a) * b
    /// Ptol = 1/b * Pcmp - a/b
    /// slope = 1/b
    /// y-intercept: a/b
    ///
    /// # Arguments
    /// * `params` - The compartment parameters
    /// * `pressure` - The compartment pressure
    ///
    /// # Returns
    /// The M0 value
    fn set(&mut self, pressure: Pressure) {
        self.pressure = pressure;
        self.m0 = (pressure - self.params.a) * self.params.b;
    }

    /// Calculate the pressure change for the compartment given the ambient pressure and the
    /// duration of the exposure.
    ///
    /// # Arguments
    /// * `ambient_pressure` - The absolute ambient pressure during the exposure for the specific
    ///   gas to which this compartment corresponds. `ambient_pressure` here should be the same as
    ///   `partial_pressure` in the `Breath` struct.
    /// * `duration` - The duration of the exposure
    ///
    /// # Returns
    /// The change in compartment pressure
    fn pressure_change(&self, ambient_pressure: &Pressure, duration: &Time) -> Pressure {
        let pressure_diff = *ambient_pressure - *WATER_VAPOR_PRESSURE - self.pressure;
        // get the ratio of times as an f64
        let time_ratio: f64 = duration.get::<Min>() / self.params.hl.get::<Min>();
        // calculate the new compartment pressure
        pressure_diff * (1.0 - 2.0_f64.powf(-time_ratio))
    }

    /// When the ambient pressure is constant throughout a duration of exposure, update the compartment
    /// pressure to account for new loading.
    ///
    /// # Arguments
    /// * `ambient_pressure` - The absolute ambient pressure during the exposure for the specific
    ///   gas to which this compartment corresponds. `ambient_pressure` here should be the same as
    ///   `partial_pressure` in the `Breath` struct.
    /// * `duration` - The duration of the exposure
    pub fn constant_pressure_update(&mut self, ambient_pressure: &Pressure, duration: &Time) {
        self.set(self.pressure + self.pressure_change(ambient_pressure, duration));
    }

    /// When the ambient pressure is different throughout a duration of exposure, linearly interpolate
    /// the compartment pressure change, and update the compartment pressure as if it were at the
    /// average ambient pressure the whole time.
    ///
    /// # Arguments
    /// * `ambient_pressure_start` - The absolute ambient pressure at the start of the exposure.
    ///   This should be the same as `partial_pressure` in the `Breath` struct.
    /// * `ambient_pressure_end` - The absolute ambient pressure at the end of the exposure.
    ///   This should be the same as `partial_pressure` in the `Breath` struct.
    /// * `duration` - The duration of the exposure
    pub fn variable_pressure_update(
        &mut self,
        ambient_pressure_start: &Pressure,
        ambient_pressure_end: &Pressure,
        duration: &Time,
    ) {
        let mean_ambient_pressure = (*ambient_pressure_start + *ambient_pressure_end) / 2.0;
        self.constant_pressure_update(&mean_ambient_pressure, duration);
    }

    /// Get the gradient factor if the compartment were instantaneously placed into an environment
    /// with the given ambient absolute pressure. A return value of 1.0 means the compartment would
    /// be at its M value. A return value of 0 means that the compartment would be at equilibrium
    /// with the environment. A return value less than zero means the compartment would be ongassing.
    ///
    /// # Arguments
    /// * `ambient_pressure` - The absolute ambient pressure to check
    ///
    /// # Returns
    /// The gradient factor. Maybe be negative.
    pub fn gradient_at(&self, ambient_pressure: &Pressure) -> Result<f64, &'static str> {
        if self.pressure == self.m0 {
            return Err("deco::buhlmann::compartment::gradient_at: compartment pressure is equal to ambient pressure");
        }
        Ok((self.pressure - *ambient_pressure).get::<Bar>()
            / (self.pressure - self.m0).get::<Bar>())
    }

    pub fn ceiling(&self, gradient: f64) -> Pressure {
        self.pressure - (self.pressure - self.m0) * gradient
    }
}

#[cfg(test)]
#[test]
fn test_params_new_valid() {
    let params = Params::new(min(3.0)).unwrap();
    assert_eq!(params.hl.get::<Min>(), 3.0);
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

#[test]
fn test_compartment_new_valid() {
    let compartment = Compartment::new(min(3.0), bar(3.0)).unwrap();
    assert_eq!(compartment.params.hl.get::<Min>(), 3.0);
    assert_approx_val!(compartment.params.a.get::<Bar>(), 1.3867225487012695, 1e-15);
    assert_approx_val!(compartment.params.b, 0.42764973081037405, 1e-15);
    assert_approx_val!(compartment.pressure.get::<Bar>(), 3.0, 1e-15);
    assert_approx_val!(compartment.m0.get::<Bar>(), 0.6899176677703485, 1e-15);
}

#[test]
fn test_compartment_new_invalid() {
    assert_eq!(
        Compartment::new(min(0.0), bar(3.0)).unwrap_err(),
        "deco::buhlmann::compartment::Params::new: half_life must be positive"
    );
}

#[test]
fn test_compartment_set() {
    let compartment = Compartment::new(min(3.0), bar(3.0)).unwrap();
    assert_approx_val!(compartment.m0, bar(0.6899176677703485), bar(1e-15));
}

#[test]
fn test_compartment_pressure_change() {
    let compartment = Compartment::new(min(3.0), bar(3.0)).unwrap();
    // stays the same when ambient pressure is the same, accounting for water vapor pressure
    assert_eq!(
        compartment
            .pressure_change(&(bar(3.0) + *WATER_VAPOR_PRESSURE), &min(100.0))
            .get::<Bar>(),
        0.0
    );
    assert_eq!(
        compartment
            .pressure_change(&(bar(4.0) + *WATER_VAPOR_PRESSURE), &min(6.0))
            .get::<Bar>(),
        0.75
    );
}

#[test]
fn test_compartment_constant_pressure_update() {
    // let mut compartment = Compartment::new(min(3.0), bar(3.0)).unwrap();
    // TODO: test that the compartment pressure is updated correctly
}

#[test]
fn test_compartment_variable_pressure_update() {
    let mut compartment = Compartment::new(min(3.0), bar(3.0)).unwrap();
    // since the update is already tested by test_constant_pressure_update, just make sure that
    // the compartment pressure is updated to the mean ambient pressure
    compartment.variable_pressure_update(
        &(bar(2.0) + *WATER_VAPOR_PRESSURE),
        &(bar(4.0) + *WATER_VAPOR_PRESSURE),
        &min(100.0),
    );
    assert_approx_val!(compartment.pressure, bar(3.0), bar(1e-15));
}

#[test]
fn test_compartment_gradient_at() {
    let compartment = Compartment::new(min(3.0), bar(3.0)).unwrap();
    assert_eq!(compartment.gradient_at(&bar(3.0)).unwrap(), 0.0);
    assert_eq!(compartment.gradient_at(&compartment.m0).unwrap(), 1.0);
    assert_eq!(
        compartment
            .gradient_at(&(compartment.pressure - (compartment.pressure - compartment.m0) / 2.0))
            .unwrap(),
        0.5
    );
}

#[test]
fn test_compartment_ceiling() {
    let tol = bar(1e-15);
    let compartment = Compartment::new(min(3.0), bar(3.0)).unwrap();
    assert_approx_val!(compartment.ceiling(1.0), compartment.m0, tol);
    assert_approx_val!(compartment.ceiling(0.0), compartment.pressure, tol);
    assert_approx_val!(
        compartment.ceiling(0.5),
        compartment.pressure - (compartment.pressure - compartment.m0) / 2.0,
        tol
    );
}