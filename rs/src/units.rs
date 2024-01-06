/// Type aliases for the units used
use dimensioned::si::{KilogramPerMeter3, Meter, MeterPerSecond2, Pascal, Liter};

pub type Density = KilogramPerMeter3<f64>;
pub type Depth = Meter<f64>;
pub type Pressure = Pascal<f64>;
pub type Acceleration = MeterPerSecond2<f64>;
pub type Volume = Liter<f64>;