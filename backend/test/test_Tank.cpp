#include "utils.h"
#include <bungee/Tank.h>

using namespace bungee;
using namespace units::literals;

TEST(Tank, Capacity) {}

TEST(Tank, CreateFull) {
    EXPECT_EQ(Aluminum80::CreateFull().pressure().value(), Aluminum80::ServicePressure.value());
}