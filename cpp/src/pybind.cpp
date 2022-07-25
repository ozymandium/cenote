#include <bungee/bungee.h>

// probably none of these includes are necessary. whatever.
#include <pybind11/chrono.h>
#include <pybind11/complex.h>
#include <pybind11/eigen.h>
#include <pybind11/functional.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

using namespace bungee;
namespace py = pybind11;

#define WRAP_UNIT(mod, cls)                                                                        \
    {                                                                                              \
        py::class_<cls>(mod, #cls).def(py::init<double>()).def("value", &cls::value);              \
    }

namespace {

// https://stackoverflow.com/a/3418285
void Replace(std::string& str, const std::string& from, const std::string& to)
{
    if (from.empty())
        return;
    size_t start_pos = 0;
    while ((start_pos = str.find(from, start_pos)) != std::string::npos) {
        str.replace(start_pos, from.length(), to);
        start_pos += to.length(); // In case 'to' contains 'from', like replacing 'x' with 'yx'
    }
}

template <typename Unit> std::string GetUnitStr()
{
    using namespace units::literals;
    std::string abbreviation = units::abbreviation(Unit(1));
    Replace(abbreviation, "_", " ");
    return abbreviation;
}

} // namespace

// clang-format off
PYBIND11_MODULE(bungee, mod) {
    // custom_units.h
    WRAP_UNIT(mod, Depth)
    WRAP_UNIT(mod, Pressure)
    WRAP_UNIT(mod, Time)
    WRAP_UNIT(mod, VolumeRate)
    mod.def("get_depth_unit_str", &GetUnitStr<Depth>);
    mod.def("get_pressure_unit_str", &GetUnitStr<Pressure>);
    mod.def("get_time_unit_str", &GetUnitStr<Time>);
    mod.def("get_volume_rate_unit_str", &GetUnitStr<VolumeRate>);
    // Tank.h
    py::enum_<Tank::Type>(mod, "Tank")
        .value("AL40", Tank::AL40)
        .value("AL80", Tank::AL80)
        .value("LP108", Tank::LP108)
        .value("D_LP108", Tank::D_LP108)
    ;
    // Mix.h
    py::class_<Mix>(mod, "Mix")
        .def(py::init<double>())
    ;
    // Plan.h
    py::class_<Plan::GradientFactor>(mod, "GradientFactor")
        .def(py::init<double, double>())
        .def_readwrite("low", &Plan::GradientFactor::low)
        .def_readwrite("high", &Plan::GradientFactor::high)
    ;
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
    py::class_<Plan::Point>(mod, "PlanPoint")
        .def(py::init<Time, Depth, const std::string&>())
        .def_readonly("time", &Plan::Point::time)
        .def_readonly("depth", &Plan::Point::depth)
        .def_readonly("tank", &Plan::Point::tank)
    ;
    py::class_<Plan>(mod, "Plan")
        .def(py::init<Water, const Plan::GradientFactor&, const Plan::Scr&, const Plan::TankLoadout&>())
        .def("set_tank", &Plan::setTank)
        .def("add_segment", &Plan::addSegment)
        .def("finalize", &Plan::finalize)
        .def("water", &Plan::water)
        .def("time", &Plan::time)
        .def("depth", &Plan::depth)
        .def("profile", &Plan::profile)
    ;
    // Water.h
    py::enum_<Water>(mod, "Water")
        .value("FRESH", Water::FRESH)
        .value("SALT", Water::SALT)
    ;
    // Result.h
    py::class_<Result::Deco>(mod, "Deco")
        .def_readonly("ceiling", &Result::Deco::ceiling)
        .def_readonly("gradient", &Result::Deco::gradient)
        .def_readonly("M0s", &Result::Deco::M0s)
        .def_readonly("tissue_pressures", &Result::Deco::tissuePressures)
        .def_readonly("ceilings", &Result::Deco::ceilings)
        .def_readonly("gradients", &Result::Deco::gradients)
    ;
    py::class_<Result>(mod, "Result")
        .def(py::init<const Plan&>())
        .def_readonly("time", &Result::time)
        .def_readonly("depth", &Result::depth)
        .def_readonly("ambient_pressure", &Result::ambientPressure)
        .def_readonly("tank_pressure", &Result::tankPressure)
        .def_readonly("deco", &Result::deco)
    ;
    // Planner.h
    mod.def("replan", &Replan);

}
// clang-format on
