#include <bungee/bungee.h>

// probably none of these includes are necessary. whatever.
#include <pybind11/chrono.h>
#include <pybind11/complex.h>
#include <pybind11/functional.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

using namespace bungee;
namespace py = pybind11;

#define WRAP_UNIT(mod, cls, name)                                                                  \
    {                                                                                              \
        py::class_<cls>(mod, #name).def(py::init<double>());                                       \
    }

namespace {

// https://stackoverflow.com/a/3418285
void replaceAll(std::string& str, const std::string& from, const std::string& to) {
    if(from.empty())
        return;
    size_t start_pos = 0;
    while((start_pos = str.find(from, start_pos)) != std::string::npos) {
        str.replace(start_pos, from.length(), to);
        start_pos += to.length(); // In case 'to' contains 'from', like replacing 'x' with 'yx'
    }
}

std::string GetVolumeRateUnitStr() {
    using namespace units::literals;
    std::string abbreviation = units::abbreviation(1_L_per_min);
    replaceAll(abbreviation, "_", " ");
    return abbreviation;
}

}


// clang-format off
PYBIND11_MODULE(bungee_py, mod) {
    // units
    WRAP_UNIT(mod, units::volume_rate::liter_per_minute_t, VolumeRateT)
    mod.def("get_volume_rate_unit_str", &GetVolumeRateUnitStr);
    WRAP_UNIT(mod, units::pressure::bar_t, PressureT)
    WRAP_UNIT(mod, units::time::minute_t, TimeT)
    WRAP_UNIT(mod, units::length::meter_t, LengthT)
    // Tank.h
    py::enum_<Tank::Type>(mod, "Tank")
        .value("AL40", Tank::AL40)
        .value("AL80", Tank::AL80)
        .value("LP108", Tank::LP108)
    ;
    // Mix.h
    py::class_<Mix>(mod, "Mix")
        .def(py::init<double>())
    ;
    // Plan.h
    py::class_<Plan::Scr>(mod, "Scr")
        .def(py::init<units::volume_rate::liter_per_minute_t, units::volume_rate::liter_per_minute_t>())
        .def_readwrite("work", &Plan::Scr::work)
        .def_readwrite("deco", &Plan::Scr::deco)
    ;
    py::class_<Plan::TankConfig>(mod, "TankConfig")
        .def(py::init<Tank::Type, units::pressure::bar_t, Mix>())
        .def_readwrite("type", &Plan::TankConfig::type)
        .def_readwrite("pressure", &Plan::TankConfig::pressure)
        .def_readwrite("mix", &Plan::TankConfig::mix)
    ;
    py::class_<Plan>(mod, "Plan")
        .def(py::init<Water, const Plan::Scr&, const Plan::TankLoadout&>())
        .def("set_tank", &Plan::setTank)
        .def("add_point", &Plan::addPointFromDuration)
        .def("finalize", &Plan::finalize)
    ;
    // Water.h
    py::enum_<Water>(mod, "Water")
        .value("FRESH", Water::FRESH)
        .value("SALT", Water::SALT)
    ;
    // Result.h
    py::class_<Result>(mod, "Result")
        .def_readwrite("time", &Result::time)
        .def_readwrite("depth", &Result::depth)
    ;

}
// clang-format on
