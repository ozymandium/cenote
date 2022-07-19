#include "utils.h"
#include <bungee/Plan.h>

using namespace bungee;
using namespace units::literals;

TEST(PlanPoint, validate)
{
    (Plan::Point{0_s, 0_m, ""}).validate();
    EXPECT_ANY_THROW(Plan::Point(-1_s, 0_m, "").validate());
    EXPECT_ANY_THROW(Plan::Point(0_s, -1_m, "").validate());
}
