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

    /// Get the compartments for the model at the given internal pressure
    ///
    /// # Arguments
    /// * `pressure` - The internal pressure at which to initialize the compartments
    ///
    /// # Returns
    /// A vector of compartments initialized at the given pressure
    pub fn compartments_at(&self, pressure: Pressure) -> Vec<Compartment> {
        let half_lives = self.half_lives();
        let mut compartments = Vec::with_capacity(half_lives.len());
        for half_life in half_lives.iter() {
            compartments.push(Compartment::new(*half_life, pressure).unwrap());
        }
        compartments
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

#[test]
fn test_zhl6a_compartments_at() {
    use crate::units::bar;

    let model = Model::Zhl16a;
    let compartments = model.compartments_at(bar(1.0));
    assert_eq!(compartments.len(), 17);
    for (i, compartment) in compartments.iter().enumerate() {
        assert_eq!(compartment.params.hl, model.half_lives()[i]);
        assert_eq!(compartment.pressure, bar(1.0));
    }
}
