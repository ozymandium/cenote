#include <bungee/Constants.h>
#include <bungee/Water.h>
#include <gtest/gtest.h>
#include <map>

using namespace bungee;
using namespace units::literals;

namespace {

template <typename Unit> void EXPECT_UNIT_NEAR(Unit unit1, Unit unit2, Unit unitTol) {
    const double val1 = units::unit_cast<double>(unit1);
    const double val2 = units::unit_cast<double>(unit2);
    const double tol = units::unit_cast<double>(unitTol);
    EXPECT_NEAR(val1, val2, tol);
}

} // namespace

TEST(Water, Pressure) {
    static constexpr units::pressure::bar_t TOL(1e-3);
    // https://bluerobotics.com/learn/pressure-depth-calculator/
    const std::map<Water, std::map<units::length::meter_t, units::pressure::bar_t>> VALUES{
        {
            Water::FRESH,
            {
                {100_m, 9.777_bar},
            },
        },
        {
            Water::SALT,
            {
                {100_m, 10.038_bar},
            },
        }};
    for (auto const& [water, vals] : VALUES) {
        for (auto const& [depth, expectedWaterPressure] : vals) {
            const auto waterPressure = WaterPressureFromDepth(depth, water);
            const auto pressure = PressureFromDepth(depth, water);
            EXPECT_UNIT_NEAR(waterPressure, expectedWaterPressure, TOL);
            EXPECT_UNIT_NEAR(pressure, waterPressure + SURFACE_PRESSURE, TOL);
        }
    }
}