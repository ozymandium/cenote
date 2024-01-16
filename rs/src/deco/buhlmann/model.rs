use crate::deco::buhlmann::compartment::Compartment;
use crate::units::{min, Pressure, Time};
use lazy_static::lazy_static;

/// A specific set of compartment half lives
///
/// <https://www.shearwater.com/wp-content/uploads/2019/05/understanding_m-values.pdf>
///
/// TODO:
/// * add a version for each fastest compartment for testing against various other implementations
/// * add other models (b, c)
pub enum Model {
    /// Compartment 1 is subdivided into 1a and 1b. 1a is 4 min, 1b is 5 min.
    /// some sources indicate it's an either/or thing, it adds conservatism to simply use both
    /// together.
    /// Subsurface uses a 5 minute fastest compartment instead of a 4 minute fastest compartment.
    ///
    /// FIXME: add a different version for each fastest compartment for testing against various
    /// other implementations
    Zhl16a,
}

impl Model {
    /// Get the half lives for the model
    ///
    /// # Returns
    /// A reference to the vector of half lives for the model
    pub fn half_lives(&self) -> &'static Vec<Time> {
        match self {
            Model::Zhl16a => &ZHL16A_HALF_LIVES,
        }
    }
}

lazy_static! {
    pub static ref ZHL16A_HALF_LIVES: Vec<Time> = vec![
        min(4.0),
        min(5.0),
        min(8.0),
        min(12.5),
        min(18.5),
        min(27.0),
        min(38.3),
        min(54.3),
        min(77.0),
        min(109.0),
        min(146.0),
        min(187.0),
        min(239.0),
        min(305.0),
        min(390.0),
        min(498.0),
        min(635.0),
    ];
}