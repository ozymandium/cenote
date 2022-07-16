#include <bungee/Water.h>

#include <pybind11/pybind11.h>

using namespace bungee;
namespace py = pybind11;

// clang-format off
PYBIND11_MODULE(bungee_py, mod) {
    // Water.h
    py::enum_<Water>(mod, "Water")
        .value("FRESH", Water::FRESH)
        .value("SALT", Water::SALT)
    ;
}
// clang-format on
