#include <bungee/Buhlmann.h>
#include <pybind11/pybind11.h>

using namespace bungee;
namespace py = pybind11;

PYBIND11_MODULE(bungee, mod) {
    py::class_<Buhlmann>(mod, "Buhlmann")
        .def(py::init<>())
    ;
}
