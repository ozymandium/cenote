#include <bungee/Constants.h>
#include <bungee/Mix.h>
#include <bungee/deco/buhlmann/Buhlmann.h>
#include <bungee/ensure.h>

#include <fmt/format.h>

using namespace units::literals;

namespace bungee::deco::buhlmann {

Buhlmann::Buhlmann(const Params& params) : _params(params)
{
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

void Buhlmann::constantPressureUpdate(const Mix::PartialPressure& partialPressure, Time duration)
{
    for (auto& compartment : _compartments) {
        compartment.constantPressureUpdate(partialPressure.N2, duration);
    }
}

void Buhlmann::variablePressureUpdate(const Mix::PartialPressure& partialPressureStart,
                                      const Mix::PartialPressure& partialPressureEnd, Time duration)
{
    for (auto& compartment : _compartments) {
        compartment.variablePressureUpdate(
            partialPressureStart.N2, partialPressureEnd.N2, duration);
    }
}

Depth Buhlmann::ceiling(const double gf) const
{
    const std::vector<Depth> vec = ceilings(gf);
    return *std::max_element(vec.begin(), vec.end());
}

std::vector<Depth> Buhlmann::ceilings(const double gf) const
{
    ensure(gf >= 0.0, "Buhlmann::ceilings: gf must be at least 0");
    ensure(gf <= 1.0, "Buhlmann::ceilings: gf must be at most 1");
    const std::vector<Pressure> m0s = M0s();
    const std::vector<Pressure> ps = pressures();
    std::vector<Depth> ret(m0s.size());
    for (size_t i = 0; i < ret.size(); ++i) {
        const Depth tolerableDepth = DepthFromPressure(m0s[i], _params.water);
        const Depth tissueDepth = DepthFromPressure(ps[i], _params.water);
        ensure(tissueDepth > tolerableDepth, "what the absolute fuck");
        ret[i] = tissueDepth - (tissueDepth - tolerableDepth) * gf;       
    }
    return ret;
}

Scalar Buhlmann::gradientAtDepth(const Depth depth) const
{
    const std::vector<Scalar> vec = gradientsAtDepth(depth);
    return *std::max_element(vec.begin(), vec.end());
}

std::vector<Scalar> Buhlmann::gradientsAtDepth(const Depth depth) const
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
