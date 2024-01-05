use dimensioned::si::{KilogramPerMeter3, KG, M3};

pub type Density = KilogramPerMeter3<f64>;

/// Helper function to convert kg/m3 to density
pub fn kg_per_m3(val: f64) -> Density {
    val * KG / M3
}
