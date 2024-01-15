pub mod buhlmann;

use crate::mix::Breath;
use crate::units::{Pressure, Time};

pub trait Deco {
    /// Expose the diver to a constant partial pressure of gas for a given duration.
    ///
    /// # Arguments
    /// * `breath` - The breathing gas
    /// * `duration` - The duration of the exposure
    fn constant_breath_update(&mut self, breath: &Breath, duration: &Time);

    /// Expose the diver to a variable partial pressure of gas for a given duration.
    /// Assume that the partial pressure changes linearly over the duration.
    ///
    /// # Arguments
    /// * `breath_start` - The breathing gas at the start of the exposure
    /// * `breath_end` - The breathing gas at the end of the exposure
    /// * `duration` - The duration of the exposure
    fn variable_breath_update(
        &mut self,
        breath_start: &Breath,
        breath_end: &Breath,
        duration: &Time,
    );

    // /// Get the lowest allowable ambient pressure for the current state of the model.
    // fn ceiling(&self) -> Pressure;
}
