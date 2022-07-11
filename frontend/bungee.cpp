#include <bungee/bungee.h>

#include <pybind11/pybind11.h>

using namespace bungee;
namespace py = pybind11;

// clang-format off
PYBIND11_MODULE(bungee, mod) {
    // Constants.h
    mod.attr("SURFACE_PRESSURE") = py::float_(SURFACE_PRESSURE);
    mod.attr("GRAVITY") = py::float_(GRAVITY);
    // Water.h
    py::enum_<Water>(mod, "Water")
        .value("FRESH", Water::FRESH)
        .value("SALT", Water::SALT)
    ;
    mod.def("get_water_density", &GetWaterDensity);
    mod.def("water_pressure_from_depth", &WaterPressureFromDepth);
    mod.def("depth_from_water_pressure", &DepthFromWaterPressure);
    mod.def("pressure_from_depth", &PressureFromDepth);
    mod.def("depth_from_pressure", &DepthFromPressure);
    // Models.h
    py::enum_<Model>(mod, "Model")
        .value("ZHL_16A", Model::ZHL_16A)
    ;
    // Buhlmann.h
    py::class_<Buhlmann>(mod, "Buhlmann")
        .def(py::init<Model>())
    ;
    // Compartment.h
    py::class_<Compartment::Params>(mod, "CompartmentParams")
        .def(py::init(&Compartment::Params::Create))
        .def_readonly("t", &Compartment::Params::t)
        .def_readonly("a", &Compartment::Params::a)
        .def_readonly("b", &Compartment::Params::b)
    ;
    py::class_<Compartment>(mod, "Compartment")
        .def(py::init<Compartment::Params>())
        .def(py::init<double>())
        .def("init", &Compartment::init)
        .def("update", &Compartment::update)
        .def("ceiling", &Compartment::ceiling)
    ;
}
// clang-format on
