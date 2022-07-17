#include <bungee/bungee.h>

// probably none of these includes are necessary. whatever.
#include <pybind11/chrono.h>
#include <pybind11/complex.h>
#include <pybind11/functional.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

using namespace bungee;
namespace py = pybind11;

#define WRAP_UNIT(mod, cls)                                                                  \
    {                                                                                              \
        py::class_<cls>(mod, #cls).def(py::init<double>());                                       \
    }

namespace {

// https://stackoverflow.com/a/3418285
void replaceAll(std::string& str, const std::string& from, const std::string& to)
{
    if (from.empty())
        return;
    size_t start_pos = 0;
    while ((start_pos = str.find(from, start_pos)) != std::string::npos) {
        str.replace(start_pos, from.length(), to);
        start_pos += to.length(); // In case 'to' contains 'from', like replacing 'x' with 'yx'
    }
}

template<typename Unit>
std::string GetUnitStr()
{
    using namespace units::literals;
    std::string abbreviation = units::abbreviation(Unit(1));
    replaceAll(abbreviation, "_", " ");
    return abbreviation;
}

} // namespace

// clang-format off
PYBIND11_MODULE(bungee_py, mod) {
    // units
    WRAP_UNIT(mod, VolumeRate)
    WRAP_UNIT(mod, Pressure)
    WRAP_UNIT(mod, Time)
    WRAP_UNIT(mod, Depth)
    mod.def("get_volume_rate_unit_str", &GetUnitStr<VolumeRate>);
    mod.def("get_pressure_rate_unit_str", &GetUnitStr<Pressure>);
    mod.def("get_time_unit_str", &GetUnitStr<Time>);
    mod.def("get_depth_unit_str", &GetUnitStr<Depth>);
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
        .def(py::init<VolumeRate, VolumeRate>())
        .def_readwrite("work", &Plan::Scr::work)
        .def_readwrite("deco", &Plan::Scr::deco)
    ;
    py::class_<Plan::TankConfig>(mod, "TankConfig")
        .def(py::init<Tank::Type, Pressure, Mix>())
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
