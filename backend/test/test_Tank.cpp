#include "utils.h"
#include <bungee/Tank.h>

using namespace bungee;
using namespace units::literals;

TEST(Tank, Capacity) {}

TEST(Tank, CreateFull)
{
    const auto al80 = Aluminum80::CreateFull();
    EXPECT_EQ(al80->pressure(), al80->servicePressure());
}
