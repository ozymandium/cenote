use crate::units::{kg_per_m3, Density};

pub enum Water {
    Fresh,
    Salt,
}

impl Water {
    /// # Water Density
    /// https://bluerobotics.com/learn/pressure-depth-calculator/#hydrostatic-water-pressure-formula
    ///
    /// ## Fresh
    /// water density varies with temperature, being more dense at lower temperatures. pure
    /// water at 0C is 1000 kg/m3. pick a value of pure water at 25C, since contaminnts
    /// generally decrease the density, and this will offset changes due to colder water.
    /// https://en.wikipedia.org/wiki/Properties_of_water
    ///
    /// ## Salt
    /// Deep salt water has higher density (1050 kg/m3) than surface water, which varies from
    /// 1020-1029 kg/m3. Pick a median value of surface seawater at 25C.
    /// https://en.wikipedia.org/wiki/Seawater
    pub fn density(&self) -> Density {
        match *self {
            Water::Fresh => kg_per_m3(997.0474),
            Water::Salt => kg_per_m3(1023.6),
        }
    }
}
