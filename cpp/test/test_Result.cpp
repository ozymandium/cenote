#include <bungee/Result.h>
#include "utils.h"

using namespace bungee;

TEST(Interpolate, Basic) {
    Eigen::ArrayXd xp, yp, x, expected;
    xp << 0, -1, 1;
    yp << 0, 1, 2;
    x << -1, 0, 0.5, 1, 1.5, 2, 3;
    expected << 0, 0, -0.5, -1, 0, 1, 1;

    const Eigen::ArrayXd y = Interpolate(xp, yp, x);

    EXPECT_EQ((y - expected).sum(), 0);

    std::cout << x << std::endl;

}