#include "utils.h"
#include <bungee/Tank.h>

using namespace bungee;
using namespace units::literals;

TEST(Tank, GetTankPressure)
{
    const auto al80 = GetTank(Tank::AL80, 3000_psi);
    EXPECT_EQ(al80->pressure(), 3000_psi);
}

TEST(Tank, VolumePressureStaticMethodRoundTrip)
{
    const Tank::Params params{.size = 10_L, .servicePressure};
}