#include "utils.h"
#include <bungee/deco/buhlmann/Compartment.h>

using namespace bungee::deco::buhlmann;
using namespace units::literals;

TEST(Params, HalfLife)
{
    const Compartment::Params params(10_min, 1.0, 1.0);
    Compartment compartment(params);
    compartment.set(0_bar);
    compartment.update(10_bar, 10_min);
    EXPECT_UNIT_NEAR(compartment.pressure(), 5_bar, 0.05_bar);
}
