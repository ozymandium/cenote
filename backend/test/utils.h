#pragma once

#include <gtest/gtest.h>
#include <units.h>

namespace {

template <typename Unit> void EXPECT_UNIT_NEAR(Unit unit1, Unit unit2, Unit unitTol)
{
    const double val1 = units::unit_cast<double>(unit1);
    const double val2 = units::unit_cast<double>(unit2);
    const double tol = units::unit_cast<double>(unitTol);
    EXPECT_NEAR(val1, val2, tol);
}

} // namespace
