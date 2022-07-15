#pragma once

#include "Plan.h"

#include <units.h>

namespace bungee {

struct Result {
   // 0.1 minutes to help avoid floating point problems
    static constexpr auto TIME_INCREMENT = units::time::second_t(6);
};

Result GetResult(const Plan& plan);

} // namespace bungee
