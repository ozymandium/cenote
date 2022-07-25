#include "utils.h"
#include <bungee/deco/buhlmann/Compartment.h>

using namespace bungee::deco::buhlmann;
using namespace units::literals;

TEST(Params, HalfLife)
{
    const Compartment::Params params(10_min);
    Compartment compartment(params);
    compartment.set(0_bar);
    compartment.constantPressureUpdate(10_bar, 10_min);
    EXPECT_UNIT_NEAR(compartment.pressure(), 5_bar, 0.05_bar);
}
