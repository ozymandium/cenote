#pragma once

namespace bungee {

class Compartment {
public:
    struct Params {
        /// Parameters a and b are computed as a function of the time constant in minutes, so the
        /// time constant is the only argument needed.
        static Params Create(double t);

        /// Half time in minutes
        double t;
        /// Coefficient `a`
        double a;
        /// Coefficient `b`
        double b;
    };

    Compartment(const Params& params);

private:
    const Params _params;
};

} // namespace bungee
