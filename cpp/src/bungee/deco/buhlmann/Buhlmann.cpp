#include <bungee/Constants.h>
#include <bungee/Mix.h>
#include <bungee/deco/buhlmann/Buhlmann.h>
#include <bungee/ensure.h>

#include <fmt/format.h>

namespace bungee::deco::buhlmann {

Buhlmann::Buhlmann(const Params& params) : _params(params)
{
    // ensure(low <= high, "gf low larger than gf high");
    ensure(0 < _params.gf_low, "gf low must be >0");
    ensure(_params.gf_low <= 1, "gf low must be at most 100%");
    ensure(0 < _params.gf_high, "gf high must be >0");
    ensure(_params.gf_high <= 1, "gf high must be at most 100%");

    const CompartmentList* compartmentList = GetCompartmentList(_params.model);
    _compartments.reserve(compartmentList->size());
    for (const units::time::minute_t halfLife : *compartmentList) {
        _compartments.emplace_back(Compartment::Params(halfLife));
    }
    ensure(_compartments.size() == compartmentList->size(), "mismatch");
}

void Buhlmann::equilibrium(const Mix::PartialPressure& partialPressure)
{
    for (auto& compartment : _compartments) {
        compartment.set(partialPressure.N2);
    }
}

void Buhlmann::setCompartmentPressures(const std::vector<Pressure> compartmentPressures)
{
    ensure(compartmentPressures.size() == compartmentCount(),
           "Buhlmann::setCompartmentPressures: wrong size");
    for (size_t i = 0; i < compartmentPressures.size(); ++i) {
        _compartments[i].set(compartmentPressures[i]);
    }
}

void Buhlmann::update(const Mix::PartialPressure& partialPressure, Time duration)
{
    for (auto& compartment : _compartments) {
        compartment.update(partialPressure.N2, duration);
    }
}

Depth Buhlmann::ceiling() const { return DepthFromPressure(M0(), _params.water); }

std::vector<Depth> Buhlmann::ceilings() const
{
    const std::vector<Pressure> m0s = M0s();
    std::vector<Depth> vec(m0s.size());
    for (size_t i = 0; i < vec.size(); ++i) {
        vec[i] = DepthFromPressure(m0s[i], _params.water);
    }
    return vec;
}

Scalar Buhlmann::gf(const Depth depth) const
{
    const std::vector<Scalar> vec = gfs(depth);
    return *std::max_element(vec.begin(), vec.end());
}

std::vector<Scalar> Buhlmann::gfs(const Depth depth) const
{
    std::vector<Scalar> vec(compartmentCount());
    const Pressure ambientPressure = PressureFromDepth(depth, _params.water);
    for (size_t i = 0; i < vec.size(); ++i) {
        vec[i] = _compartments[i].gf(ambientPressure);
    }
    return vec;
}

std::vector<Pressure> Buhlmann::M0s() const
{
    std::vector<Pressure> vec(compartmentCount());
    for (size_t i = 0; i < vec.size(); ++i) {
        vec[i] = _compartments[i].M0();
    }
    return vec;
}

Pressure Buhlmann::M0() const
{
    const std::vector<Pressure> vec = M0s();
    return *std::max_element(vec.begin(), vec.end());
}

std::vector<Pressure> Buhlmann::pressures() const
{
    std::vector<Pressure> vec(compartmentCount());
    for (size_t i = 0; i < vec.size(); ++i) {
        vec[i] = _compartments[i].pressure();
    }
    return vec;
}

} // namespace bungee::deco::buhlmann
