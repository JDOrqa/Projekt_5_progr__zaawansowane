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
static inline long double parseLongDouble(const std::string &s)
{
    std::istringstream iss(s);
    long double val = 0;
    if (!(iss >> val) || !iss.eof())
    {
        throw std::invalid_argument("Niepoprawna liczba: " + s);
    }
    return val;
}

// Kahan add dla long double
struct Kahan {
    long double sum = 0.0L;
    long double c = 0.0L;
    void add(long double value) noexcept {
        long double y = value - c;
        long double t = sum + y;
        c = (t - sum) - y;
        sum = t;
    }
};
enum class Mode { DYNAMIC, STATIC };
int main(int argc, char *argv[])
{
    try
    {
        uint64_t numSteps = 0;
        unsigned threadCount = 0;
        Mode mode = Mode::DYNAMIC;
        uint64_t userChunk = 0;

        if (argc >= 3)
        {
            numSteps = parseUint64(argv[1]);
            threadCount = static_cast<unsigned>(parseUint64(argv[2]));
            if (argc > 3) {
                std::string modeStr = argv[3];
                mode = (modeStr == "static") ? Mode::STATIC : Mode::DYNAMIC;
            }
            if (argc > 4) userChunk = parseUint64(argv[4]);
        }
