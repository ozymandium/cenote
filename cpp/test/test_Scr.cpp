#include "utils.h"
#include <bungee/Scr.h>

using namespace bungee;
using namespace units::literals;

TEST(Scr, ScrAtDepth)
{
    const auto SCR = 0.75_cu_ft_per_min;
    // 1% error (due to depth/pressure approximation below, not in the code)
    constexpr auto TOLERANCE = SCR * 1e-2;
    auto scr1 = ScrAtDepth(SCR, 0_ft, Water::FRESH);
    EXPECT_UNIT_NEAR(scr1, SCR, TOLERANCE);
    auto scr2 = ScrAtDepth(SCR, 10.4_m, Water::FRESH);
    EXPECT_UNIT_NEAR(scr2, 2 * SCR, TOLERANCE);
    auto scr3 = ScrAtDepth(SCR, 10.1_m, Water::SALT);
    EXPECT_UNIT_NEAR(scr3, 2 * SCR, TOLERANCE);
    auto scr4 = ScrAtDepth(SCR, 20.8_m, Water::FRESH);
    EXPECT_UNIT_NEAR(scr4, 3 * SCR, TOLERANCE);
    auto scr5 = ScrAtDepth(SCR, 20.2_m, Water::SALT);
    EXPECT_UNIT_NEAR(scr5, 3 * SCR, TOLERANCE);
}

TEST(Scr, ScrFromSacExact)
{
    auto al80 = GetFullTank(Tank::AL80);
    auto sac = al80.servicePressure() / 1_min;
    auto scr = ScrFromSac(sac, al80);
    EXPECT_EQ(scr, al80.serviceVolume() / 1_min);
}

TEST(Scr, ScrSacRoundTrip)
{
    auto sac = 30_psi_per_min;
    auto al80 = GetFullTank(Tank::AL80);
    auto scrFromSac = ScrFromSac(sac, al80);
    auto sacFromScr = SacFromScr(scrFromSac, al80);
    EXPECT_EQ(sacFromScr, sac);
}

// TEST()