#pragma once

namespace bungee {

class Compartment {
public:
    struct Params {
        /// Half time in minutes
        const double t;
        /// Coefficient `a`
        const double a;
        /// Coefficient `b`
        const double b;
    };

    Compartment(const Params& params);

private:
    const Params _params;
};

} // namespace bungee
