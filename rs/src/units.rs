pub use uom::si::f64::{
    Acceleration, Length as Depth, MassDensity as Density, Pressure, PressureRate, Time, Volume,
    VolumeRate,
};

pub type Min = uom::si::time::minute;
pub type MPerS2 = uom::si::acceleration::meter_per_second_squared;
pub type KgPerM3 = uom::si::mass_density::kilogram_per_cubic_meter;
pub type Atm = uom::si::pressure::atmosphere;
pub type Bar = uom::si::pressure::bar;
pub type Psi = uom::si::pressure::pound_force_per_square_inch;
pub type BarPerMin = uom::si::pressure_rate::bar_per_minute;
pub type PsiPerMin = uom::si::pressure_rate::psi_per_minute;
pub type Meter = uom::si::length::meter;
pub type Liter = uom::si::volume::liter;
pub type CuFt = uom::si::volume::cubic_foot;
pub type CuFtPerMin = uom::si::volume_rate::cubic_foot_per_minute;

pub fn min(value: f64) -> Time {
    Time::new::<Min>(value)
}
pub fn m_per_s2(value: f64) -> Acceleration {
    Acceleration::new::<MPerS2>(value)
}
pub fn kg_per_m3(value: f64) -> Density {
    Density::new::<KgPerM3>(value)
}
pub fn atm(value: f64) -> Pressure {
    Pressure::new::<Atm>(value)
}
pub fn bar(value: f64) -> Pressure {
    Pressure::new::<Bar>(value)
}
pub fn psi(value: f64) -> Pressure {
    Pressure::new::<Psi>(value)
}
pub fn bar_per_min(value: f64) -> PressureRate {
    PressureRate::new::<BarPerMin>(value)
}
pub fn psi_per_min(value: f64) -> PressureRate {
    PressureRate::new::<PsiPerMin>(value)
}
pub fn meter(value: f64) -> Depth {
    Depth::new::<Meter>(value)
}
pub fn liter(value: f64) -> Volume {
    Volume::new::<Liter>(value)
}
pub fn cuft(value: f64) -> Volume {
    Volume::new::<CuFt>(value)
}
pub fn cuft_per_min(value: f64) -> VolumeRate {
    VolumeRate::new::<CuFtPerMin>(value)
}
