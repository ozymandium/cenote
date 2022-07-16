#include <bungee/Mix.h>
#include <bungee/ensure.h>

namespace bungee {

Mix::Mix(const double fO2) 
{
    set(fO2);
}

Mix::PartialPressure Mix::partialPressure(units::length::meter_t depth, Water water) const
{
    const units::pressure::bar_t pressure = PressureFromDepth(depth, water);
    return PartialPressure{
        .O2 = _fO2 * pressure,
        .N2 = _fN2 * pressure,
    };
}

void Mix::set(const double fO2)
{
    _fO2 = fO2;
    _fN2 = 1.0 - fO2;
    ensure((0 < _fO2) && (_fO2 <= 1.0), "invalid O2 fraction");
    ensure((0 <= _fN2) && (_fN2 < 1.0), "invalid N2 fraction");
    ensure(_fO2 + _fN2 == 1.0, "total gas fraction not 100%");
}

const Mix AIR(0.20946);
const Mix::PartialPressure SURFACE_AIR_PP(AIR.partialPressure(units::length::meter_t(0.),
                                                              Water::FRESH));

} // namespace bungee