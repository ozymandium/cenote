mod compartment;
mod gf;
mod model;

use crate::deco::buhlmann::compartment::Compartment;
use crate::deco::buhlmann::model::Model;
use crate::deco::Deco;
use crate::mix::{Breath, PartialPressure};
use crate::units::{Pressure, Time};
use crate::water::Water;

/// Holds all tissue compartments.
/// When multiple gases are used, there is one set of compartments for each gas.
struct Compartments {
    /// Nitrogen compartments for each half life.
    n2: Vec<Compartment>,
}

impl Compartments {
    /// Create a new set of compartments that have reached equilibrium with the given breathing gas.
    ///
    /// # Arguments
    /// * `model` - The decompression model
    fn new(model: &Model, partial_pressure: &PartialPressure) -> Self {
        let mut n2 = Vec::with_capacity(model.half_lives().len());
        for half_life in model.half_lives().iter() {
            n2.push(Compartment::new(*half_life, partial_pressure.n2).unwrap());
        }
        Compartments { n2 }
    }

    fn constant_pressure_update(&mut self, partial_pressure: &PartialPressure, duration: &Time) {
        for compartment in self.n2.iter_mut() {
            compartment.constant_pressure_update(&partial_pressure.n2, duration);
        }
    }

    fn variable_pressure_update(
        &mut self,
        partial_pressure_start: &PartialPressure,
        partial_pressure_end: &PartialPressure,
        duration: &Time,
    ) {
        for compartment in self.n2.iter_mut() {
            compartment.variable_pressure_update(
                &partial_pressure_start.n2,
                &partial_pressure_end.n2,
                duration,
            );
        }
    }
}

pub struct Buhlmann {
    /// The compartments for each gas for each half life.
    compartments: Compartments,
    /// The maximum ambient pressure that's been experienced.
    max_ambient_pressure: Pressure,
}

impl Buhlmann {
    /// Create a new Buhlmann decompression model. Choose a default model.
    fn new(breath: &Breath) -> Self {
        let model = Model::Zhl16a;
        Buhlmann {
            compartments: Compartments::new(&model, &breath.partial_pressure),
            max_ambient_pressure: breath.ambient_pressure,
        }
    }
}

impl Deco for Buhlmann {
    fn constant_breath_update(&mut self, breath: &Breath, duration: &Time) {
        self.compartments
            .constant_pressure_update(&breath.partial_pressure, duration);
    }

    fn variable_breath_update(
        &mut self,
        breath_start: &Breath,
        breath_end: &Breath,
        duration: &Time,
    ) {
        // TODO: ensure mix is the same for breath_start and breath_end
        self.compartments.variable_pressure_update(
            &breath_start.partial_pressure,
            &breath_end.partial_pressure,
            duration,
        );
    }

    // fn ceiling(&self) -> Pressure {
    //     unimplemented!();
    // }
}

#[test]
fn test_zhl6a_compartments_new() {
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

#[test]
fn test_compartments_constant_pressure_update() {
    use crate::mix::SURFACE_AIR;
    use crate::units::{bar, min};

    let breath = &SURFACE_AIR;
    let model = Model::Zhl16a;
    let duration = min(10.0);

    let mut compartments = Compartments::new(&model, &breath.partial_pressure);
    compartments.constant_pressure_update(&breath.partial_pressure, &duration);

    let mut expected_compartments = Compartments::new(&model, &breath.partial_pressure);
    for (i, expected_compartment) in expected_compartments.n2.iter_mut().enumerate() {
        expected_compartment.constant_pressure_update(&breath.partial_pressure.n2, &duration);
        assert_eq!(expected_compartment.pressure, compartments.n2[i].pressure);
    }
}

#[test]
fn test_compartments_variable_pressure_update() {
    use crate::mix::SURFACE_AIR;
    use crate::units::{bar, min};

    let breath_start = &SURFACE_AIR;
    let breath_end = &SURFACE_AIR;
    let model = Model::Zhl16a;
    let duration = min(10.0);

    let mut compartments = Compartments::new(&model, &breath_start.partial_pressure);
    compartments.variable_pressure_update(
        &breath_start.partial_pressure,
        &breath_end.partial_pressure,
        &duration,
    );

    let mut expected_compartments = Compartments::new(&model, &breath_start.partial_pressure);
    for (i, expected_compartment) in expected_compartments.n2.iter_mut().enumerate() {
        expected_compartment.variable_pressure_update(
            &breath_start.partial_pressure.n2,
            &breath_end.partial_pressure.n2,
            &duration,
        );
        assert_eq!(expected_compartment.pressure, compartments.n2[i].pressure);
    }
}

#[test]
fn test_buhlmann_new() {
    use crate::mix::SURFACE_AIR;
    use crate::units::bar;

    let breath = &SURFACE_AIR;
    let buhlmann = Buhlmann::new(&breath);
    assert_eq!(buhlmann.compartments.n2.len(), 17);
    for (i, compartment) in buhlmann.compartments.n2.iter().enumerate() {
        assert_eq!(compartment.params.hl, Model::Zhl16a.half_lives()[i]);
        assert_eq!(compartment.pressure, breath.partial_pressure.n2);
    }
    assert_eq!(buhlmann.max_ambient_pressure, breath.ambient_pressure);
}

#[test]
fn test_buhlmann_constant_breath_update() {
    use crate::mix::SURFACE_AIR;
    use crate::units::{bar, min};

    let breath = &SURFACE_AIR;
    let model = Model::Zhl16a;
    let duration = min(10.0);

    let mut buhlmann = Buhlmann::new(&breath);
    buhlmann.constant_breath_update(&breath, &duration);

    let mut expected_compartments = Compartments::new(&model, &breath.partial_pressure);
    for (i, expected_compartment) in expected_compartments.n2.iter_mut().enumerate() {
        expected_compartment.constant_pressure_update(&breath.partial_pressure.n2, &duration);
        assert_eq!(
            expected_compartment.pressure,
            buhlmann.compartments.n2[i].pressure
        );
    }
}

#[test]
fn test_buhlmann_variable_breath_update() {
    use crate::mix::SURFACE_AIR;
    use crate::units::{bar, min};

    let breath_start = &SURFACE_AIR;
    let breath_end = &SURFACE_AIR;
    let model = Model::Zhl16a;
    let duration = min(10.0);

    let mut buhlmann = Buhlmann::new(&breath_start);
    buhlmann.variable_breath_update(&breath_start, &breath_end, &duration);

    let mut expected_compartments = Compartments::new(&model, &breath_start.partial_pressure);
    for (i, expected_compartment) in expected_compartments.n2.iter_mut().enumerate() {
        expected_compartment.variable_pressure_update(
            &breath_start.partial_pressure.n2,
            &breath_end.partial_pressure.n2,
            &duration,
        );
        assert_eq!(
            expected_compartment.pressure,
            buhlmann.compartments.n2[i].pressure
        );
    }
}
