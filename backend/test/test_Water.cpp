#include "utils.h"
#include <bungee/Constants.h>
#include <bungee/Water.h>
#include <map>

using namespace bungee;
using namespace units::literals;

TEST(Water, Pressure)
{
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