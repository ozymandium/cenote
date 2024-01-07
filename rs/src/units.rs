pub use uom::si::f64::{Acceleration, MassDensity as Density, Pressure, Length as Depth};


// use uom::si::pressure::{atmosphere, bar, psi};

pub fn m_per_s2(value: f64) -> Acceleration {
    use uom::si::acceleration::meter_per_second_squared;
    Acceleration::new::<meter_per_second_squared>(value)
}

pub fn kg_per_m3(value: f64) -> Density {
    use uom::si::mass_density::kilogram_per_cubic_meter;
    Density::new::<kilogram_per_cubic_meter>(value)
}

pub fn atm(value: f64) -> Pressure {
    use uom::si::pressure::atmosphere;
    Pressure::new::<atmosphere>(value)
}

pub fn bar(value: f64) -> Pressure {
    use uom::si::pressure::bar;
    Pressure::new::<bar>(value)
}

pub fn psi(value: f64) -> Pressure {
    use uom::si::pressure::pound_force_per_square_inch;
    Pressure::new::<pound_force_per_square_inch>(value)
}

pub fn meter(value: f64) -> Depth {
    use uom::si::length::meter;
    Depth::new::<meter>(value)
}
