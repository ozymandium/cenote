use crate::constants::{FRESH_WATER_DENSITY, GRAVITY, SALT_WATER_DENSITY, SURFACE_PRESSURE};
use crate::units::{Density, Depth, Pressure};

/// The type of water
pub enum Water {
    Fresh,
    Salt,
}

impl Water {
    /// Water Density
    ///
    /// https://bluerobotics.com/learn/pressure-depth-calculator/#hydrostatic-water-pressure-formula
    pub fn density(&self) -> Density {
        match *self {
            Water::Fresh => *FRESH_WATER_DENSITY,
            Water::Salt => *SALT_WATER_DENSITY,
        }
    }

    /// Pressure from the water at a given depth, not including surface pressure.
    pub fn rel_pressure_at_depth(&self, depth: Depth) -> Pressure {
        self.density() * (*GRAVITY) * depth
    }

    /// Absolute pressure at a given depth, including surface pressure.
    pub fn abs_pressure_at_depth(&self, depth: Depth) -> Pressure {
        self.rel_pressure_at_depth(depth) + (*SURFACE_PRESSURE)
    }

    /// Depth from the surface at a given relative pressure.
    pub fn depth_at_rel_pressure(&self, pressure: Pressure) -> Depth {
        pressure / (self.density() * (*GRAVITY))
    }

    /// Depth from the surface at a given absolute pressure.
    pub fn depth_at_abs_pressure(&self, pressure: Pressure) -> Depth {
        self.depth_at_rel_pressure(pressure - (*SURFACE_PRESSURE))
    }
}

#[cfg(test)]
mod test_helpers {
    use dimensioned::Dimensioned;
    use std::ops::Sub;

    #[cfg(test)]
    pub fn assert_approx<T>(lhs: T, rhs: T, tol: T)
        where
            T: Dimensioned<Value = f64> + Sub<Output = T> + Into<f64>,
        {
            // since dimensioned quantities implement each individual unit as a type, we know that all
            // quantities are of the same type, so we can convert them to f64 without conversion
            let lhs_val: f64 = lhs.into();
            let rhs_val: f64 = rhs.into();
            let tol_val: f64 = tol.into();
        
            assert!((lhs_val - rhs_val).abs() <= tol_val);
    }    
}

#[test]
fn test_density() {
    use dimensioned::si::{KG, M3};
    assert_eq!(Water::Fresh.density(), 997.0474 * KG / M3);
    assert_eq!(Water::Salt.density(), 1023.6 * KG / M3);
}

#[test]
fn test_pressure_and_depth() {
    use dimensioned::si::{BAR, M};
    use test_helpers::assert_approx;

    struct Expectation {
        water: Water,
        depth: Depth,
        rel_pressure: Pressure,
    }
    impl Expectation {
        fn abs_pressure(&self) -> Pressure {
            self.rel_pressure + (*SURFACE_PRESSURE)
        }
    }

    let expectations = vec![
        Expectation {
            water: Water::Fresh,
            depth: 0.0 * M,
            rel_pressure: 0.0 * BAR,
        },
        Expectation {
            water: Water::Salt,
            depth: 0.0 * M,
            rel_pressure: 0.0 * BAR,
        },
        Expectation {
            water: Water::Fresh,
            depth: 100.0 * M,
            rel_pressure: 9.777 * BAR,
        },
        Expectation {
            water: Water::Salt,
            depth: 100.0 * M,
            rel_pressure: 10.038 * BAR,
        },
    ];

    let depth_tol: Depth = 1e-3 * M;
    let pressure_tol: Pressure = 1e-3 * BAR;

    for expectation in expectations {
        let water: &Water = &expectation.water;
        assert_approx(
            water.rel_pressure_at_depth(expectation.depth),
            expectation.rel_pressure,
            pressure_tol
        );
        // assert_approx(
        //     water.abs_pressure_at_depth(expectation.depth),
        //     expectation.abs_pressure(),
        //     pressure_tol
        // );
        // assert_approx(
        //     water.depth_at_rel_pressure(expectation.rel_pressure),
        //     expectation.depth,
        //     depth_tol
        // );
        // assert_approx(
        //     water.depth_at_abs_pressure(expectation.abs_pressure()),
        //     expectation.depth,
        //     depth_tol
        // );
    }
}