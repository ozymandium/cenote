pub mod buhlmann;

use crate::mix::PartialPressure;
use crate::units::{Pressure, Time};

// pub trait Deco {
//     /// Create a new decompression model.
//     ///
//     /// # Arguments
//     /// * `partial_pressure` - The partial pressure of the breathing gas at which the model should
//     ///   be initialized, assuming perfect equilibrium
//     fn new(partial_pressure: PartialPressure) -> Self;

//     /// Expose the diver to a constant partial pressure of gas for a given duration.
//     ///
//     /// # Arguments
//     /// * `partial_pressure` - The absolute partial pressure of the breathing gas
//     /// * `duration` - The duration of the exposure
//     fn constant_pressure_update(&mut self, &partial_pressure: PartialPressure, &duration: Time);

//     /// Expose the diver to a variable partial pressure of gas for a given duration.
//     /// Assume that the partial pressure changes linearly over the duration.
//     ///
//     /// # Arguments
//     /// * `partial_pressure_start` - The absolute partial pressure of the breathing gas at the start
//     ///   of the exposure
//     /// * `partial_pressure_end` - The absolute partial pressure of the breathing gas at the end of
//     ///   the exposure
//     /// * `duration` - The duration of the exposure
//     fn variable_pressure_update(
//         &mut self,
//         partial_pressure_start: &PartialPressure,
//         partial_pressure_end: &PartialPressure,
//         duration: &Time,
//     );

//     /// Get the lowest allowable ambient pressure for the current state of the model.
//     fn ceiling(&self) -> Pressure;
// }
