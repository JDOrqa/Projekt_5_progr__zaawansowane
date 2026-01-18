#include <iostream>
#include <vector>
#include <thread>
#include <chrono>
#include <iomanip>
#include <cmath>
#include <cstdint>
#include <string>
#include <sstream>
#include <stdexcept>
#include <atomic>
#include <algorithm>
#include <limits>
#ifndef M_PI
constexpr long double PI_FALLBACK = 3.141592653589793238462643383279502884L;
#else
constexpr long double PI_FALLBACK = static_cast<long double>(M_PI);
#endif

static inline uint64_t parseUint64(const std::string &s)
{
    std::istringstream iss(s);
    uint64_t val = 0;
    if (!(iss >> val) || !iss.eof())
    {
        throw std::invalid_argument("Niepoprawna liczba całkowita: " + s);
    }
    return val;
}
