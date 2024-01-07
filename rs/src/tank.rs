use crate::units::{atm, liter, psi, Pressure, Volume};

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
                empty_volume: liter(5.8),
                service_pressure: psi(3_000.0),
                z: 1.045,
            },
            TankKind::Al80 => TankSpec {
                empty_volume: liter(11.1),
                service_pressure: psi(3_000.0),
                z: 1.0337,
            },
            TankKind::Lp108 => TankSpec {
                empty_volume: liter(17.0),
                service_pressure: psi(2640.0),
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
        self.empty_volume * pressure / (self.z * atm(1.0))
    }

    /// The pressure of the gas in the tank at the specified volume. Pressure is relative to
    /// ambient pressure, so the returned pressure does not include the gas at 1 atm which remains
    /// in the tank when the pressure relative to surface conditions is zero.
    fn pressure_at_volume(&self, volume: Volume) -> Pressure {
        volume / self.empty_volume * self.z * atm(1.0)
    }

    /// The volume of gas in the tank at the service pressure.
    fn service_volume(&self) -> Volume {
        self.volume_at_pressure(self.service_pressure)
    }
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
            pressure: psi(0.0),
            volume: liter(0.0),
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
fn test_spec_volume_pressure_round_trip() {
    use crate::assert_approx_val;
    use crate::units::cuft;
    let spec = TankSpec::new(TankKind::Al80);
    assert_eq!(spec.volume_at_pressure(psi(0.0)), liter(0.0));
    assert_eq!(spec.pressure_at_volume(liter(0.0)), psi(0.0));
    assert_approx_val!(spec.volume_at_pressure(psi(3000.0)), cuft(77.4), cuft(0.1));
    assert_approx_val!(spec.pressure_at_volume(cuft(77.4)), psi(3000.0), psi(1.0));
}

#[test]
fn test_al40() {
    use crate::assert_approx_val;
    use crate::units::cuft;
    let spec = TankSpec::new(TankKind::Al40);
    assert_approx_val!(spec.service_volume(), cuft(40.0), cuft(0.1));
}

#[test]
fn test_lp_108() {
    use crate::assert_approx_val;
    use crate::units::cuft;
    let spec = TankSpec::new(TankKind::Lp108);
    assert_approx_val!(spec.service_volume(), cuft(108.0), cuft(0.2));
}

#[test]
fn test_tank_new() {
    let tank = Tank::new(TankKind::Al40);
    assert_eq!(tank.volume, liter(0.0));
    assert_eq!(tank.pressure, psi(0.0));
}

#[test]
fn test_tank_new_at_pressure() {
    let spec = TankSpec::new(TankKind::Al40);
    let tank = Tank::new_at_pressure(TankKind::Al40, spec.service_pressure);
    assert_eq!(tank.volume, spec.service_volume());
    assert_eq!(tank.pressure, spec.service_pressure);
}

#[test]
fn test_tank_new_at_volume() {
    let spec = TankSpec::new(TankKind::Al40);
    let tank = Tank::new_at_volume(TankKind::Al40, spec.service_volume());
    assert_eq!(tank.volume, spec.service_volume());
    assert_eq!(tank.pressure, spec.service_pressure);
}

#[test]
fn test_tank_set_pressure() {
    use crate::assert_approx_val;
    use crate::units::cuft;
    let mut tank = Tank::new(TankKind::Al40);
    tank.set_pressure(psi(3000.0));
    assert_approx_val!(tank.volume, cuft(40.0), cuft(0.1));
    assert_approx_val!(tank.pressure, psi(3000.0), psi(1.0));
}

#[test]
fn test_tank_set_volume() {
    use crate::assert_approx_val;
    use crate::units::cuft;
    let mut tank = Tank::new(TankKind::Al40);
    tank.set_volume(cuft(40.0));
    assert_approx_val!(tank.volume, cuft(40.0), cuft(0.1));
    assert_approx_val!(tank.pressure, psi(3000.0), psi(1.0));
}

#[test]
fn test_tank_decrease_volume() {
    use crate::assert_approx_val;
    use crate::units::cuft;
    let mut tank = Tank::new(TankKind::Al40);
    tank.set_volume(cuft(40.0));
    tank.decrease_volume(cuft(10.0));
    assert_approx_val!(tank.volume, cuft(30.0), cuft(0.1));
    assert_approx_val!(tank.pressure, psi(2250.0), psi(1.0));
}

#[test]
fn test_tank_decrease_pressure() {
    use crate::assert_approx_val;
    use crate::units::cuft;
    let mut tank = Tank::new(TankKind::Al40);
    tank.set_pressure(psi(3000.0));
    tank.decrease_pressure(psi(1000.0));
    assert_approx_val!(tank.volume, cuft(26.67), cuft(0.1));
    assert_approx_val!(tank.pressure, psi(2000.0), psi(1.0));
}
