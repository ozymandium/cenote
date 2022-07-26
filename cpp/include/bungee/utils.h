#include "Constants.h"

#include <Eigen/Dense>

namespace bungee {

size_t GetNumPoints(Time duration);

/// \brief 1d interpolation
///
/// \param[in] data
///    [ x1, x2, ..., xM ]
///    [ y1, y2, ..., yM ]
///
/// \param[in] x
///    [ x1, x2, ..., xN ]
///
/// \return interpolated y data corresponding to x
Eigen::VectorXd Interpolate(Eigen::Ref<const Eigen::VectorXd> xp,
                            Eigen::Ref<const Eigen::VectorXd> yp,
                            Eigen::Ref<const Eigen::VectorXd> x);

inline std::string str(Depth unit) { return units::length::to_string(unit); }
inline std::string str(Time unit) { return units::time::to_string(unit); }

} // namespace bungee
