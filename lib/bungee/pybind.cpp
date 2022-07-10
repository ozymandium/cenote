#include <bungee/Buhlmann.h>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

using namespace bungee;
namespace py = pybind11;

// clang-format off
PYBIND11_MODULE(bungee, mod) {
    py::enum_<Model>(mod, "Model")
        .value("ZHL_16A", Model::ZHL_16A)
    ;
    py::class_<Buhlmann>(mod, "Buhlmann")
        .def(py::init<Model>())
    ;
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
    // py::bind_vector<ModelParams>(mod, "ModelParams");
    // mod.def("get_model_params", &GetModelParams);
}
// clang-format on
