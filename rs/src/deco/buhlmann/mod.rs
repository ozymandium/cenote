mod compartment;
mod gf;
mod models;

// use crate::mix::PartialPressure;

// struct Params {
//     water: Water,
//     model: Model,
// }

// /// Holds all tissue compartments.
// /// When multiple gases are used, there is one set of compartments for each gas.
// struct Compartments {
//     /// Nitrogen compartments for each half life.
//     n2: Vec<Compartment>,
// }

// impl Compartments {
//     /// Create a new set of compartments for the given model and pressure.
//     ///
//     /// # Arguments
//     /// * `model` - The decompression model
//     /// * `pressure` - The pressure at which to initialize the compartments
//     fn new(model: Model, partial_pressure: PartialPressure) -> Self {
//         let compartments = {
//             let mut compartments = Vec::with_capacity(model.half_lives().len());
//             for (i, half_life) in model.half_lives().iter().enumerate() {
//                 compartments.push(Compartment::new(*half_life, pressure).unwrap());
//             }
//             compartments
//         };
//         Compartments {
//             compartments,
//         }
//     }
// }

// pub struct Buhlmann {
//     params: Params,
//     compartments: Compartments
// }

// impl Buhlmann {
//     pub fn new(water: Water, model: Model, partial_pressure: PartialPressure) -> Self {
//         let compartments = {

//         };
//         Buhlmann {
//             params: Params { water, model },
//             compartments,
//         }
//     }
// }