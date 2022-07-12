#include "utils.h"
#include <bungee/Tank.h>

using namespace bungee;
using namespace units::literals;

TEST(Tank, GetEmptyTank) {
    const auto al80 = GetEmptyTank(Tank::AL80);
    EXPECT_EQ(al80.pressure(), 0_bar);
    EXPECT_EQ(al80.volume(), 0_L);
}

TEST(Tank, AL80Full) {
    const auto al80 = GetFullTank(Tank::AL80);
    EXPECT_EQ(al80.pressure(), 3000_psi);
    EXPECT_UNIT_NEAR(units::volume::cubic_foot_t(al80.volume()), 77.4_cu_ft, 0.05_cu_ft);
}

TEST(Tank, LP108Full) {
    const auto lp108 = GetFullTank(Tank::LP108);
    EXPECT_EQ(lp108.pressure(), 2640_psi);
    EXPECT_UNIT_NEAR(units::volume::cubic_foot_t(lp108.volume()), 108_cu_ft, 0.2_cu_ft);
}

TEST(Tank, GetTankAtPressure)
{
    const auto al80 = GetTankAtPressure(Tank::AL80, 1789_psi);
    EXPECT_EQ(al80.pressure(), 1789_psi);
}

TEST(Tank, GetTankAtVolume) {
    const auto al80 = GetTankAtVolume(Tank::AL80, 42_cu_ft);
    EXPECT_EQ(al80.volume(), 42_cu_ft);
}

// TEST(Tank, VolumePressureStaticMethodRoundTrip)
// {
//     const Tank::Params params{.size = 10_L, .servicePressure};
// }