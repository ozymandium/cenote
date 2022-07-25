#include "utils.h"
#include <bungee/Result.h>
#include <bungee/utils.h>

using namespace bungee;
using namespace units::literals;

// move this
TEST(Interpolate, Basic)
{
    Eigen::VectorXd xp(3), yp(3), x(5), expected(5);
    xp << 0, 1, 2;
    yp << 0, -1, 1;
    x << 0, 0.5, 1, 1.5, 2;
    expected << 0, -0.5, -1, 0, 1;
    const Eigen::VectorXd y = Interpolate(xp, yp, x);
    for (size_t i = 0; i < x.size(); ++i) {
        EXPECT_NEAR(y[i], expected[i], 1e-12);
    }
}

TEST(Interpolate, FailBeyondEdges) {}

TEST(Interpolate, IncreasingXp) {}

TEST(Usage, NegativeDuration) { EXPECT_ANY_THROW(Usage(-1_s, 0_m, 1_L_per_min, Water::FRESH)); }

TEST(Usage, NegativeScr) { EXPECT_ANY_THROW(Usage(60_s, 0_m, -1_L_per_min, Water::FRESH)); }

TEST(Usage, Surface) { EXPECT_EQ(Usage(60_s, 0_m, 10_L_per_min, Water::SALT), 10_L); }

TEST(Usage, Depth) { EXPECT_UNIT_NEAR(Usage(60_s, 10_m, 10_L_per_min, Water::SALT), 20_L, 0.1_L); }
