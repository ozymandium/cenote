use dimensioned::si::{L, PSI, ATM};
use crate::units::{Volume, Pressure};
use crate::constants::SURFACE_PRESSURE;

pub enum TankKind {
    Al40,
    Al80,
    Lp108,
}

struct TankSpec {
    /// The volume of gas in the tank when it is empty / at ambient pressure
    empty_volume: Volume,
    /// The rated maximum pressure of the tank relative to ambient pressure
    service_pressure: Pressure,
    /// The z-factor
    z: f64,
}

impl TankSpec {
    fn new(kind: TankKind) -> Self {
        match kind {
            TankKind::Al40 => TankSpec {
                empty_volume: 5.8 * L,
                service_pressure: 3_000 * PSI,
                z: 1.045,
            },
            TankKind::Al80 => TankSpec {
                empty_volume: 11.1 * L,
                service_pressure: 3_000 * PSI,
                z: 1.0337,
            },
            TankKind::Lp108 => TankSpec {
                empty_volume: 17 * L,
                service_pressure: 2640 * PSI,
                z: 1.0,
            },
        }
    }

    /// The volume of gas in the tank at the specified pressure. Pressure is relative to
    /// ambient pressure, so the returned volume does not include the gas at 1 atm which remains in
    /// the tank when the pressure relative to surface conditions is zero.
    ///
    /// # FIXME
    /// - should use of 1 atm here be changed to surface pressure?
    fn volume_at_pressure(&self, pressure: Pressure) -> Volume {
        self.empty_volume * pressure / (self.z * (1 * ATM))
    }

    /// The pressure of the gas in the tank at the specified volume. Pressure is relative to
    /// ambient pressure, so the returned pressure does not include the gas at 1 atm which remains
    /// in the tank when the pressure relative to surface conditions is zero.
    fn pressure_at_volume(&self, volume: Volume) -> Pressure {
        volume / self.empty_volume * self.z * (1 * ATM)
    }

    // fn service_volume(&self) -> Volume {
    //     self.empty_volume * self.z
    // }
}

pub struct Tank {
    spec: TankSpec,

    /// The pressure of the gas in the tank relative to ambient pressure.
    ///
    /// # FIXME:
    /// This does not account for ambient pressure at depth, but rather always considers
    /// the tank to be at the surface.
    pressure: Pressure,

    /// Volume of gas in the tank which corresponds to relative pressures above 1 atm at the
    /// surface. This does not include the gas at 1 atm which remains in the tank when the pressure
    /// relative to surface conditions is zero.
    volume: Volume,
}

impl Tank {
    /// Creates a new empty tank
    pub fn new(kind: TankKind) -> Self {
        Tank {
            spec: TankSpec::new(kind),
            pressure: 0.0 * PSI,
            volume: 0.0 * L,
        }
    }

    /// Creates a new tank with the specified pressure
    pub fn new_at_pressure(kind: TankKind, pressure: Pressure) -> Self {
        let mut tank = Tank::new(kind);
        tank.set_pressure(pressure);
        tank
    }

    pub fn new_at_volume(kind: TankKind, volume: Volume) -> Self {
        let mut tank = Tank::new(kind);
        tank.set_volume(volume);
        tank
    }

    /// Updates the pressure and volume of the tank
    pub fn set_pressure(&mut self, pressure: Pressure) {
        self.pressure = pressure;
        self.volume = self.spec.volume_at_pressure(pressure);
    }

    pub fn set_volume(&mut self, volume: Volume) {
        self.volume = volume;
        self.pressure = self.spec.pressure_at_volume(volume);
    }

    pub fn decrease_volume(&mut self, diff: Volume) {
        self.set_volume(self.volume - diff);
    }

    pub fn decrease_pressure(&mut self, diff: Pressure) {
        self.set_pressure(self.pressure - diff);
    }
}

#[test]
fn test_spec_volume_at_pressure() {
    use dimensioned::si::{L, PSI};
    use crate::units::Volume;

    let spec = TankSpec::new(TankKind::Al80);
    assert_eq!(spec.volume_at_pressure(0.0 * PSI), 0.0 * L);
    assert_eq!(spec.volume_at_pressure(1000.0 * PSI), 0.0 * L);
    assert_eq!(spec.volume_at_pressure(3000.0 * PSI), 11.1 * L);
}
