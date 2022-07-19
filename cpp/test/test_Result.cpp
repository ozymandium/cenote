#include "utils.h"
#include <bungee/Result.h>

using namespace bungee;

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
