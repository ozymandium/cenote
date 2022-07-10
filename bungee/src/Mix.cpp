#include <bungee/Mix.h>

namespace bungee {

Mix::Mix(const double fO2) : fO2(fO2), fN2(1.0 - fO2) {
    assert((0 < fO2) && (fO2 <= 1.0));
    assert((0 <= fN2) && (fN2 < 1.0));
    assert(fO2 + fN2 == 1.0);
}

Mix::PartialPressure Mix::partialPresure(double depth, Water water) const {
    // pressure in bar
    const double pressure = PressureFromDepth(depth, water);
    return PartialPressure{
        .O2 = fO2 * pressure,
        .N2 = fN2 * pressure,
    };
}

} // namespace bungee