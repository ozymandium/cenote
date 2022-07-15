#include <bungee/Mix.h>
#include <bungee/ensure.h>

namespace bungee {

Mix::Mix(const double fO2) : fO2(fO2), fN2(1.0 - fO2)
{
    ensure((0 < fO2) && (fO2 <= 1.0), "invalid O2 fraction");
    ensure((0 <= fN2) && (fN2 < 1.0), "invalid N2 fraction");
    ensure(fO2 + fN2 == 1.0, "total gas fraction not 100%");
}

Mix::PartialPressure Mix::partialPressure(units::length::meter_t depth, Water water) const
{
    const units::pressure::bar_t pressure = PressureFromDepth(depth, water);
    return PartialPressure{
        .O2 = fO2 * pressure,
        .N2 = fN2 * pressure,
    };
}

const Mix AIR(0.20946);
const Mix::PartialPressure SURFACE_AIR_PP(AIR.partialPressure(units::length::meter_t(0.),
                                                              Water::FRESH));

} // namespace bungee