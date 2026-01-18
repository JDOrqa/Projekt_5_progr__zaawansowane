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
else
        {
            // Interaktywny fallback
            std::string line;
            std::cout << "Podaj liczbe podzialow (np. 100000000): ";
            if (!std::getline(std::cin, line) || line.empty()) return 0;
            numSteps = parseUint64(line);

            std::cout << "Podaj liczbe watkow (np. 4): ";
            if (!std::getline(std::cin, line) || line.empty()) return 0;
            threadCount = static_cast<unsigned>(parseUint64(line));

            std::cout << "Tryb [dynamic/static] (enter = dynamic): ";
            if (std::getline(std::cin, line) && !line.empty()) {
                mode = (line == "static") ? Mode::STATIC : Mode::DYNAMIC;
            }

            if (mode == Mode::DYNAMIC) {
                std::cout << "Rozmiar chunk (enter = auto): ";
                if (std::getline(std::cin, line) && !line.empty()) {
                    userChunk = parseUint64(line);
                }
            }
        }

        if (numSteps == 0)
        {
            std::cerr << "Liczba podziałów musi być > 0\n";
            return 1;
        }
        if (threadCount == 0)
        {
            std::cerr << "Liczba wątków musi być > 0\n";
            return 1;
        }
        if (threadCount > numSteps) threadCount = static_cast<unsigned>(numSteps);

        const long double h = 1.0L / static_cast<long double>(numSteps);

        std::vector<long double> partialSums(threadCount, 0.0L);
        std::vector<std::thread> threads;
        threads.reserve(threadCount);

        auto tStart = std::chrono::high_resolution_clock::now();

        if (mode == Mode::DYNAMIC)
        {
            std::atomic<uint64_t> nextIndex(0);
            const uint64_t defaultChunk = std::max<uint64_t>(1, numSteps / (static_cast<uint64_t>(threadCount) * 128ULL));
            const uint64_t chunk = (userChunk > 0) ? userChunk : defaultChunk;

            for (unsigned t = 0; t < threadCount; ++t)
            {
                threads.emplace_back([t, &nextIndex, chunk, numSteps, h, &partialSums]() {
                    auto f = [](long double x) -> long double {
                        return 4.0L / (1.0L + x * x);
                    };

                    Kahan k{};
                    while (true)
                    {
                        uint64_t i = nextIndex.fetch_add(chunk, std::memory_order_relaxed);
                        if (i >= numSteps) break;
                        uint64_t end = std::min<uint64_t>(i + chunk, numSteps);
                        for (uint64_t idx = i; idx < end; ++idx)
                        {
                            long double x = (static_cast<long double>(idx) + 0.5L) * h;
                            k.add(f(x));
                        }
                    }
                    partialSums[t] = k.sum;
                });
            }
        }
        else // STATIC
        {
            const uint64_t baseChunk = numSteps / threadCount;
            const uint64_t remainder = numSteps % threadCount;
            for (unsigned t = 0; t < threadCount; ++t)
            {
                const uint64_t start = static_cast<uint64_t>(t) * baseChunk + std::min<uint64_t>(t, remainder);
                const uint64_t end = start + baseChunk + (t < remainder ? 1 : 0);

                threads.emplace_back([t, start, end, h, &partialSums]() {
                    auto f = [](long double x) -> long double {
                        return 4.0L / (1.0L + x * x);
                    };

                    Kahan k{};
                    for (uint64_t idx = start; idx < end; ++idx)
                    {
                        long double x = (static_cast<long double>(idx) + 0.5L) * h;
                        k.add(f(x));
                    }
                    partialSums[t] = k.sum;
                });
            }
        }

        for (auto &th : threads) if (th.joinable()) th.join();

        // Finalne scalanie wyników (Kahan)
        Kahan finalK;
        for (unsigned t = 0; t < threadCount; ++t)
        {
            finalK.add(partialSums[t]);
        }

        long double pi = finalK.sum * h;

        auto tEnd = std::chrono::high_resolution_clock::now();
        std::chrono::duration<long double> elapsed = tEnd - tStart;

        std::cout << std::fixed << std::setprecision(15);
        std::cout << "Tryb: " << (mode == Mode::DYNAMIC ? "dynamic" : "static") << '\n';
        std::cout << "Wynik przyblizenia PI: " << pi << '\n';
        std::cout << "Blad bezwzgl.: " << std::scientific << std::setprecision(12)
            << std::abs(pi - PI_FALLBACK) << '\n';
        std::cout << "Czas wykonania: " << std::fixed << std::setprecision(9)
            << elapsed.count() << " s\n";
        std::cout << "Liczba podzialow: " << numSteps << ", liczba watkow: " << threadCount << '\n';
        if (mode == Mode::DYNAMIC) std::cout << "Rozmiar chunk: " << (userChunk > 0 ? userChunk : std::max<uint64_t>(1, numSteps / (static_cast<uint64_t>(threadCount) * 128ULL))) << '\n';

        return 0;
    }
    catch (const std::exception &ex)
    {
        std::cerr << "Blad: " << ex.what() << '\n';
        return 2;
    }
}
