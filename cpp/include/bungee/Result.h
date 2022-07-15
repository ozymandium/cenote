#pragma once

#include "Plan.h"

#include <units.h>

namespace bungee {

class Result {
public:
    // 0.1 minutes to help avoid floating point problems
    static constexpr auto TIME_INC = units::time::second_t(6);

    Result(const Plan& plan);

private:
    const Plan _plan;
};

} // namespace bungee
