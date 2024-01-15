mod compartment;
mod gf;
mod model;

use crate::deco::buhlmann::compartment::Compartment;
use crate::deco::buhlmann::model::Model;
use crate::deco::Deco;
use crate::mix::Breath;
use crate::units::{Pressure, Time};
use crate::water::Water;

/// Holds all tissue compartments.
/// When multiple gases are used, there is one set of compartments for each gas.
struct Compartments {
    /// Nitrogen compartments for each half life.
    n2: Vec<Compartment>,
}

impl Compartments {
    /// Create a new set of compartments for the given model and pressure.
    ///
    /// # Arguments
    /// * `model` - The decompression model
    /// * `breath` - The breathing gas
    fn new(model: &Model, breath: &Breath) -> Self {
        let mut n2 = Vec::with_capacity(model.half_lives().len());
        for half_life in model.half_lives().iter() {
            n2.push(Compartment::new(*half_life, breath.partial_pressure.n2).unwrap());
        }
        Compartments { n2 }
    }
}

pub struct Buhlmann {
    /// The compartments for each gas for each half life.
    compartments: Compartments,
    /// The maximum ambient pressure that's been experienced.
    max_ambient_pressure: Pressure,
}

impl Deco for Buhlmann {
    /// Create a new Buhlmann decompression model. Choose a default model.
    fn new(breath: &Breath) -> Self {
        let model = Model::Zhl16a;
        Buhlmann {
            compartments: Compartments::new(&model, breath),
            max_ambient_pressure: breath.ambient_pressure,
        }
    }

    // fn constant_breath_update(&mut self, breath: &Breath, duration: &Time) {
    //     for compartment in self.compartments.n2.iter_mut() {
    //         compartment.constant_pressure_update(breath.partial_pressure.n2, duration);
    //     }
    // }

    // fn variable_breath_update(
    //     &mut self,
    //     breath_start: &Breath,
    //     breath_end: &Breath,
    //     duration: &Time,
    // ) {
    //     for compartment in self.compartments.n2.iter_mut() {
    //         compartment.variable_pressure_update(
    //             breath_start.partial_pressure.n2,
    //             breath_end.partial_pressure.n2,
    //             duration,
    //         );
    //     }
    // }

    // fn ceiling(&self) -> Pressure {
    //     unimplemented!();
    // }
}

#[test]
fn test_zhl6a_compartments_at() {
    use crate::mix::SURFACE_AIR;
    use crate::units::bar;

    let model = Model::Zhl16a;
    // copy surface air partial pressure
    let breath = &SURFACE_AIR;
    let compartments = Compartments::new(&model, &breath);
    assert_eq!(compartments.n2.len(), 17);
    for (i, compartment) in compartments.n2.iter().enumerate() {
        assert_eq!(compartment.params.hl, model.half_lives()[i]);
        assert_eq!(compartment.pressure, breath.partial_pressure.n2);
    }
}
