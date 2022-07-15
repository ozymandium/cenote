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

TEST(Usage, OutOfOrder)
{
    EXPECT_ANY_THROW(Usage(Plan::Point{1_s, 0_m, ""}, Plan::Point{0_s, 0_m, ""}, 
                     1_L_per_min, Water::FRESH));
}

TEST(Usage, Surface)
{
    Plan::Point p1{10_s, 0_m, ""};
    Plan::Point p2{70_s, 0_m, ""};
    EXPECT_EQ(Usage(p1, p2, 10_L_per_min, Water::SALT), 10_L);
}

TEST(Usage, ConstDepth)
{
    Plan::Point p1{10_s, 10_m, ""};
    Plan::Point p2{70_s, 10_m, ""};
    EXPECT_UNIT_NEAR(Usage(p1, p2, 10_L_per_min, Water::SALT), 20_L, 0.1_L);
}

TEST(Usage, AvgDepth)
{
    Plan::Point p1{120_min, 10_m, ""};
    Plan::Point p2{121_min, 30_m, ""};
    EXPECT_UNIT_NEAR(Usage(p1, p2, 10_L_per_min, Water::SALT), 30_L, 0.2_L);
}
