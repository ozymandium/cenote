mod compartment;
mod gf;
mod model;

use crate::deco::buhlmann::compartment::Compartment;
use crate::deco::buhlmann::model::Model;
use crate::mix::PartialPressure;
use crate::water::Water;
// use crate::deco::Deco;
use crate::units::{Pressure, Time};

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
    /// * `pressure` - The pressure at which to initialize the compartments
    fn new(model: &Model, partial_pressure: &PartialPressure) -> Self {
        let mut n2 = Vec::with_capacity(model.half_lives().len());
        for half_life in model.half_lives().iter() {
            n2.push(Compartment::new(*half_life, partial_pressure.n2).unwrap());
        }
        Compartments { n2 }
    }
}

pub struct Buhlmann {
    /// The compartments for each gas for each half life.
    compartments: Compartments,
    /// The current ambient pressure.
    ambient_pressure: Pressure,
}

// impl Deco for Buhlmann {
//     /// Create a new Buhlmann decompression model. Choose a default model.
//     fn new(partial_pressure: &PartialPressure) -> Self {
//         let model = Model::Zhl16a;
//         Buhlmann {
//             compartments: Compartments::new(model, partial_pressure),
//         }
//     }

//     fn constant_pressure_update(&mut self, partial_pressure: PartialPressure, duration: Time) {
//         for compartment in self.compartments.n2.iter_mut() {
//             compartment.constant_pressure_update(partial_pressure.n2, duration);
//         }
//     }

//     fn variable_pressure_update(
//         &mut self,
//         partial_pressure_start: PartialPressure,
//         partial_pressure_end: PartialPressure,
//         duration: Time,
//     ) {
//         for compartment in self.compartments.n2.iter_mut() {
//             compartment.variable_pressure_update(
//                 partial_pressure_start.n2,
//                 partial_pressure_end.n2,
//                 duration,
//             );
//         }
//     }

//     fn ceiling(&self) -> Pressure {
//         unimplemented!();
//     }
// }

#[test]
fn test_zhl6a_compartments_at() {
    use crate::mix::SURFACE_AIR;
    use crate::units::bar;

    let model = Model::Zhl16a;
    // copy surface air partial pressure
    let breath = &SURFACE_AIR;
    let compartments = Compartments::new(&model, &breath.partial_pressure);
    assert_eq!(compartments.n2.len(), 17);
    for (i, compartment) in compartments.n2.iter().enumerate() {
        assert_eq!(compartment.params.hl, model.half_lives()[i]);
        assert_eq!(compartment.pressure, breath.partial_pressure.n2);
    }
}
