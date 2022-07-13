#include <bungee/Scr.h>
#include <gtest/gtest.h>

using namespace bungee;
using namespace units::literals;

TEST(CustomUnits, volume_rate_unit)
{
    const auto x = 1_L_per_min;
    const units::volume_rate::cubic_meter_per_second_t y = x * units::dimensionless::dimensionless_t(3);
    EXPECT_EQ(y.value() / x.value(), 3);

}

// TEST(Scr, ScrAtDepthZero)
// {
//     const auto surfaceScr = 10_L_per_min;
//     const auto depthScr = ScrAtDepth(surfaceScr, 0_m, Water::FRESH);
//     EXPECT_EQ(surfaceScr, depthScr);
// }

TEST(Scr, ScrAtDepthNonZero) {}
