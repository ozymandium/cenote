#include <bungee/bungee.h>

#include <pybind11/pybind11.h>

using namespace bungee;
namespace py = pybind11;

// clang-format off
PYBIND11_MODULE(bungee, mod) {
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
    // Buhlmann.h
    py::class_<Buhlmann>(mod, "Buhlmann")
        .def(py::init<Model>())
    ;
}
// clang-format on
