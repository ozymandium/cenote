#pragma once

#include <gtest/gtest.h>
#include <bungee/custom_units.h>

namespace {

template <typename Unit> void EXPECT_UNIT_NEAR(Unit unit1, Unit unit2, Unit unitTol)
{
    const double val1 = units::unit_cast<double>(unit1);
    const double val2 = units::unit_cast<double>(unit2);
    const double tol = units::unit_cast<double>(unitTol);
    EXPECT_NEAR(val1, val2, tol);
}

// TODO: enable_if conversion so you don't have to overload for different type
template <typename Unit1, typename Unit2>
void EXPECT_UNIT_NEAR(Unit1 unit1, Unit2 unit2, Unit1 unitTol)
{
    const double val1 = units::unit_cast<double>(unit1);
    const double val2 = units::unit_cast<double>(Unit1(unit2));
    const double tol = units::unit_cast<double>(unitTol);
    EXPECT_NEAR(val1, val2, tol);
}

// TODO: enable_if conversion so you don't have to overload for different type
template <typename Unit1, typename Unit2>
void EXPECT_UNIT_NEAR(Unit1 unit1, Unit2 unit2, Unit2 unitTol)
{
    const double val1 = units::unit_cast<double>(Unit2(unit1));
    const double val2 = units::unit_cast<double>(unit2);
    const double tol = units::unit_cast<double>(unitTol);
    EXPECT_NEAR(val1, val2, tol);
}

} // namespace
