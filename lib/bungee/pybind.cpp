#include <bungee/Buhlmann.h>
#include <pybind11/pybind11.h>

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
}
// clang-format on
