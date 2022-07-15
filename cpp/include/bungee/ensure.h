#pragma once

#include <stdexcept>

namespace {

inline void ensure(const bool cond, const std::string& msg)
{
    if (!cond) {
        throw std::logic_error(msg);
    }
}

} // namespace
