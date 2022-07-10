#pragma once

namespace bungee {

class Mix {
public:

    struct PartialPressure {
        double pO2;
        double pN2;
        double depth;
        Water
    };

    explicit Mix(double pO2);

    Mix atDepth()

    /// Fraction of oxygen, 0.0 - 1.0 [unitless]
    const double _pO2;
    /// Fraction of nitrogen, 0.0 - 1.0 [unitless]
    const double _pN2;
};

}