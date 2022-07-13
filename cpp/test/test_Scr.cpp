#include "utils.h"
#include <bungee/Scr.h>

using namespace bungee;
using namespace units::literals;

TEST(CustomUnits, volume_rate_unit)
{
    auto x = 1_L_per_min;
    units::volume_rate::cubic_meter_per_second_t y = x * 3;
    EXPECT_EQ(y / x, 3);
}

TEST(Scr, ScrAtDepthZero)
{
    auto surfaceScr = 10_L_per_min;
    auto depthScr = ScrAtDepth(surfaceScr, 0_m, Water::FRESH);
    EXPECT_EQ(surfaceScr, depthScr);
}

TEST(Scr, ScrAtDepthNonZero)
{
    auto surfaceScr = 10_L_per_min;
    auto depthScr = ScrAtDepth(surfaceScr, 10_m, Water::SALT);
    EXPECT_UNIT_NEAR(surfaceScr * 2, depthScr, 0.1_L_per_min);
}

TEST(Scr, ScrFromSac)
{
    auto al80 = GetFullTank(Tank::AL80);
    auto sac = al80.servicePressure() / 1_min;
    auto scr = ScrFromSac(sac, al80);
    EXPECT_EQ(scr, al80.serviceVolume() / 1_min);
}

TEST(Scr, RoundTrip)
{
    auto sac = 30_psi_per_min;
    auto al80 = GetFullTank(Tank::AL80);
    auto scrFromSac = ScrFromSac(sac, al80);
    auto sacFromScr = SacFromScr(scrFromSac, al80);
    EXPECT_EQ(sacFromScr, sac);
}