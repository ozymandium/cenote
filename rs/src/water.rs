use crate::constants::{GRAVITY, SURFACE_PRESSURE};
use crate::units::{kg_per_m3, Density, Depth, Pressure, VolumeRate};

/// The type of water
pub enum Water {
    Fresh,
    Salt,
}

/// TODO: when implementing variable surface pressure and water temperature, make pressure
/// conversion functions part of a class `Environment` that includes Water, temperature, and
/// surface pressure.
impl Water {
    /// Water Density
    ///
    /// <https://bluerobotics.com/learn/pressure-depth-calculator/#hydrostatic-water-pressure-formula>
    ///
    /// # Fresh water density
    /// water density varies with temperature, being more dense at lower temperatures. pure
    /// water at 0C is 1000 kg/m3. pick a value of pure water at 25C, since contaminants
    /// generally decrease the density, and this will offset changes due to colder water.
    /// <https://en.wikipedia.org/wiki/Properties_of_water>
    ///
    /// # Salt water density
    /// Deep salt water has higher density (1050 kg/m3) than surface water, which varies from
    /// 1020-1029 kg/m3. Pick a median value of surface seawater at 25C.
    /// <https://en.wikipedia.org/wiki/Seawater>
    pub fn density(&self) -> Density {
        match *self {
            Water::Fresh => kg_per_m3(997.0474),
            Water::Salt => kg_per_m3(1023.6),
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

    /// Converts the surface consumption rate to a consumption rate at a given depth.
    pub fn scr_at_depth(&self, scr: VolumeRate, depth: Depth) -> VolumeRate {
        let abs_pressure = self.abs_pressure_at_depth(depth);
        let scaling = abs_pressure / (*SURFACE_PRESSURE);
        scr * scaling
    }
}

#[test]
fn test_pressure_and_depth() {
    use crate::assert_approx_ref;
    use crate::units::{bar, meter};

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
            depth: meter(0.0),
            rel_pressure: bar(0.0),
        },
        Expectation {
            water: Water::Salt,
            depth: meter(0.0),
            rel_pressure: bar(0.0),
        },
        Expectation {
            water: Water::Fresh,
            depth: meter(100.0),
            rel_pressure: bar(9.777),
        },
        Expectation {
            water: Water::Salt,
            depth: meter(100.0),
            rel_pressure: bar(10.038),
        },
    ];

    let depth_tol: Depth = meter(1e-2);
    let pressure_tol: Pressure = bar(1e-3);

    for expectation in expectations {
        let water: &Water = &expectation.water;
        assert_approx_ref!(
            &water.rel_pressure_at_depth(expectation.depth),
            &expectation.rel_pressure,
            &pressure_tol
        );
        assert_approx_ref!(
            &water.abs_pressure_at_depth(expectation.depth),
            &expectation.abs_pressure(),
            &pressure_tol
        );
        assert_approx_ref!(
            &water.depth_at_rel_pressure(expectation.rel_pressure),
            &expectation.depth,
            &depth_tol
        );
        assert_approx_ref!(
            &water.depth_at_abs_pressure(expectation.abs_pressure()),
            &expectation.depth,
            &depth_tol
        );
    }
}

#[test]
fn test_scr_at_depth() {
    use crate::assert_approx_ref;
    use crate::units::{cuft_per_min, meter};

    let scr: VolumeRate = cuft_per_min(0.75);
    // 1% error (due to depth/pressure approximation below, not in the code)
    let scr_tol: VolumeRate = scr * 1e-2;

    struct Expectation {
        water: Water,
        depth: Depth,
        scr: VolumeRate,
    }

    let expectations = vec![
        Expectation {
            water: Water::Fresh,
            depth: meter(0.0),
            scr: scr,
        },
        Expectation {
            water: Water::Salt,
            depth: meter(0.0),
            scr: scr,
        },
        Expectation {
            water: Water::Fresh,
            depth: meter(10.4),
            scr: scr * 2.0,
        },
        Expectation {
            water: Water::Salt,
            depth: meter(10.1),
            scr: scr * 2.0,
        },
        Expectation {
            water: Water::Fresh,
            depth: meter(20.8),
            scr: scr * 3.0,
        },
        Expectation {
            water: Water::Salt,
            depth: meter(20.2),
            scr: scr * 3.0,
        },
    ];

    for expectation in expectations {
        let water: &Water = &expectation.water;
        assert_approx_ref!(
            &water.scr_at_depth(scr, expectation.depth),
            &expectation.scr,
            &scr_tol
        );
    }
}
