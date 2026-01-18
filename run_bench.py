#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skrypt do automatyzacji testów programu PI Calculator
Uruchamia program z różnymi parametrami i generuje wykresy
"""

import argparse
import subprocess
import re
import csv
import os
import sys
import time
import statistics
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
# Regex dla twojego programu - DOSTOSOWANY!
TIME_REGEX = re.compile(r"Czas wykonania:\s*([0-9]+\.[0-9]+)\s*s", re.IGNORECASE)
PI_REGEX = re.compile(r"Wynik przyblizenia PI:\s*([0-9]+\.[0-9]+)", re.IGNORECASE)
ERROR_REGEX = re.compile(r"Blad bezwzgl\.:\s*([0-9]+\.[0-9eE\-]+)", re.IGNORECASE)
CHUNK_REGEX = re.compile(r"Rozmiar chunk:\s*([0-9]+)", re.IGNORECASE)

def parse_output(output):
    """Parsuje output programu i wyciąga potrzebne dane"""
    result = {
        'time': None,
        'pi_value': None,
        'error': None,
        'chunk': None,
        'mode': None,
        'raw_output': output
    }
    
    # Szukaj czasu
    m = TIME_REGEX.search(output)
    if m:
        result['time'] = float(m.group(1))
    
    # Szukaj wartości PI
    m = PI_REGEX.search(output)
    if m:
        result['pi_value'] = float(m.group(1))
    
    # Szukaj błędu
    m = ERROR_REGEX.search(output)
    if m:
        result['error'] = float(m.group(1))
    
    # Szukaj chunk size
    m = CHUNK_REGEX.search(output)
    if m:
        result['chunk'] = int(m.group(1))
    
    # Szukaj trybu
    if "Tryb: dynamic" in output:
        result['mode'] = 'dynamic'
    elif "Tryb: static" in output:
        result['mode'] = 'static'
    
    return result

def run_single_test(exe_path, steps, threads, mode='dynamic', chunk=None, timeout=600):
    """Uruchamia pojedynczy test"""
    # Buduj komendę
    cmd = [exe_path, str(steps), str(threads), mode]
    if chunk is not None:
        cmd.append(str(chunk))
    
    print(f"  Uruchamianie: {' '.join(cmd)}")
    
    try:
        # Uruchom program
        start_time = time.time()
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            timeout=timeout,
            encoding='utf-8',
            errors='ignore'  # Ignoruj problemy z kodowaniem
        )
        elapsed = time.time() - start_time
        
        # Połącz stdout i stderr
        output = result.stdout + "\n" + result.stderr
        
        if result.returncode != 0:
            print(f"    BŁĄD (kod {result.returncode}): {output[:200]}...")
            return None
        
        # Parsuj output
        parsed = parse_output(output)
        parsed['exit_code'] = result.returncode
        parsed['real_time'] = elapsed
        
        if parsed['time'] is None:
            print(f"    NIE ZNALEZIONO CZASU! Output: {output[:200]}...")
            return None
        
        print(f"    Czas: {parsed['time']:.3f}s, PI: {parsed['pi_value']:.15f}, Błąd: {parsed['error']:.2e}")
        return parsed
        
    except subprocess.TimeoutExpired:
        print(f"    TIMEOUT po {timeout}s")
        return None
    except Exception as e:
        print(f"    BŁĄD WYJĄTKU: {e}")
        return None
        def run_benchmark_suite(config):
    """Przeprowadza kompleksowe testy"""
    results = []
    
    print(f"\n{'='*60}")
    print(f"ROZPOCZĘCIE TESTOWANIA")
    print(f"{'='*60}")
    print(f"Program: {config['exe_path']}")
    print(f"Tryb: {config['mode']}")
    print(f"Chunk: {config.get('chunk', 'auto')}")
    print(f"Powtórzenia: {config['repeats']}")
    print(f"Interwały: {config['steps_list']}")
    print(f"Wątki: od 1 do {config['max_threads']}")
    print(f"{'='*60}\n")
    
    total_tests = len(config['steps_list']) * config['max_threads'] * config['repeats']
    test_counter = 0
    
    for steps in config['steps_list']:
        print(f"\n INTERWAŁY: {steps:,}")
        print("-" * 40)
        
        for threads in range(1, config['max_threads'] + 1):
            print(f"\n  Wątki: {threads}")
            
            # Uruchom kilka razy dla lepszej statystyki
            times = []
            pi_values = []
            errors = []
            
            for repeat in range(config['repeats']):
                test_counter += 1
                print(f"   Powtórzenie {repeat + 1}/{config['repeats']}...", end="")
                
                result = run_single_test(
                    config['exe_path'],
                    steps,
                    threads,
                    config['mode'],
                    config.get('chunk'),
                    config['timeout']
                )
                
                if result:
                    times.append(result['time'])
                    pi_values.append(result['pi_value'])
                    errors.append(result['error'])
                    print(f" OK")
                else:
                    print(f" FAILED")
                
                # Krótka pauza między testami
                if repeat < config['repeats'] - 1:
                    time.sleep(0.5)
            
            # Zapisz mediany jeśli mamy wyniki
            if times:
                results.append({
                    'steps': steps,
                    'threads': threads,
                    'time_median': statistics.median(times),
                    'time_mean': statistics.mean(times),
                    'time_std': statistics.stdev(times) if len(times) > 1 else 0,
                    'pi_median': statistics.median(pi_values),
                    'error_median': statistics.median(errors),
                    'samples': len(times),
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
    
    print(f"\n{'='*60}")
    print(f"TESTOWANIE ZAKOŃCZONE")
    print(f"Wykonano {test_counter} testów")
    print(f"{'='*60}")
    
    return results
    def save_results(results, csv_path):
    """Zapisuje wyniki do CSV"""
    df = pd.DataFrame(results)
    df.to_csv(csv_path, index=False, encoding='utf-8')
    print(f"\n Zapisano wyniki do: {csv_path}")
    print(f"   Rekordów: {len(df)}")
    return df

def plot_results(df, output_png):
    """Generuje wykresy"""
    if df.empty:
        print("Brak danych do wykresu!")
        return
    
    # Wykres 1: Czas vs Wątki dla różnych interwałów
    plt.figure(figsize=(14, 8))
    
    colors = ['blue', 'green', 'red', 'purple', 'orange']
    markers = ['o', 's', '^', 'D', 'v']
    
    steps_groups = df.groupby('steps')
    
    for idx, (steps, group) in enumerate(steps_groups):
        color = colors[idx % len(colors)]
        marker = markers[idx % len(markers)]
        
        group = group.sort_values('threads')
        plt.errorbar(
            group['threads'],
            group['time_median'],
            yerr=group['time_std'],
            color=color,
            marker=marker,
            markersize=8,
            linewidth=2,
            capsize=5,
            label=f'{steps:,} interwałów',
            alpha=0.8
        )
    
    plt.xlabel('Liczba wątków', fontsize=12)
    plt.ylabel('Czas wykonania [s]', fontsize=12)
    plt.title('Wydajność obliczeń PI - zależność czasu od liczby wątków', 
              fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=11, loc='upper right')
    plt.xticks(range(0, int(df['threads'].max()) + 1, 5))
    
    # Znajdź optymalne wartości
    for steps in df['steps'].unique():
        subset = df[df['steps'] == steps]
        if not subset.empty:
            min_time_idx = subset['time_median'].idxmin()
            optimal = subset.loc[min_time_idx]
            plt.scatter(optimal['threads'], optimal['time_median'], 
                       color='red', s=200, zorder=5, 
                       edgecolors='black', linewidth=2)
            plt.annotate(f"Opt: {int(optimal['threads'])} wątków\n{optimal['time_median']:.2f}s", 
                        (optimal['threads'], optimal['time_median']),
                        xytext=(10, -20), textcoords='offset points',
                        fontsize=9, fontweight='bold',
                        bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7))
    
    plt.tight_layout()
    plt.savefig(output_png, dpi=300, bbox_inches='tight')
    print(f" Zapisano wykres do: {output_png}")

# Wykres 2: Speedup
    plt.figure(figsize=(12, 6))
    
    for idx, (steps, group) in enumerate(steps_groups):
        color = colors[idx % len(colors)]
        group = group.sort_values('threads')
        
        # Czas dla 1 wątku jako baseline
        single_thread_time = group[group['threads'] == 1]['time_median'].values[0]
        speedup = single_thread_time / group['time_median']
        
        plt.plot(group['threads'], speedup,
                color=color, marker=markers[idx % len(markers)],
                linewidth=2, markersize=6,
                label=f'{steps:,} interwałów')
        
        # Idealne przyspieszenie (linia przerywana)
        plt.plot(group['threads'], group['threads'],
                color=color, linestyle='--', alpha=0.3)
    
    plt.xlabel('Liczba wątków', fontsize=12)
    plt.ylabel('Przyspieszenie (Speedup)', fontsize=12)
    plt.title('Przyspieszenie równoległe obliczeń PI', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=11)
    plt.xticks(range(0, int(df['threads'].max()) + 1, 5))
    plt.tight_layout()
    
    speedup_png = output_png.replace('.png', '_speedup.png')
    plt.savefig(speedup_png, dpi=300, bbox_inches='tight')
    print(f" Zapisano wykres speedup do: {speedup_png}")
    
    plt.show()

def main():
    parser = argparse.ArgumentParser(
        description=' Automatyzacja testów programu obliczającego PI metodą całkowania',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Przykłady użycia:
  python benchmark.py --exe LiczbaPi.exe --steps 100000000 1000000000 --max-threads 16
  python benchmark.py --exe pi_calculator.exe --mode static --repeats 5 --out-csv wyniki.csv
        """
    )
    
    parser.add_argument('--exe', required=True,
                       help='Ścieżka do programu wykonywalnego (np. LiczbaPi.exe)')
    parser.add_argument('--steps', nargs='+', type=int,
                       default=[100000000, 500000000, 1000000000],
                       help='Lista wartości podziałów (domyślnie: 100M, 500M, 1B)')
    parser.add_argument('--max-threads', type=int, default=32,
                       help='Maksymalna liczba wątków do przetestowania (domyślnie: 32)')
    parser.add_argument('--mode', choices=['dynamic', 'static'], default='dynamic',
                       help='Tryb przydziału pracy (domyślnie: dynamic)')
    parser.add_argument('--chunk', type=int,
                       help='Rozmiar chunk dla trybu dynamic (puste = auto)')
    parser.add_argument('--repeats', type=int, default=3,
                       help='Liczba powtórzeń każdego testu (domyślnie: 3)')
    parser.add_argument('--timeout', type=int, default=300,
                       help='Maksymalny czas wykonania jednego testu w sekundach (domyślnie: 300)')
    parser.add_argument('--out-csv', default='benchmark_results.csv',
                       help='Plik wynikowy CSV (domyślnie: benchmark_results.csv)')
    parser.add_argument('--out-png', default='benchmark_chart.png',
                       help='Plik z wykresem PNG (domyślnie: benchmark_chart.png)')
    parser.add_argument('--skip-plot', action='store_true',
                       help='Pomiń generowanie wykresów')
    
    args = parser.parse_args()
    
    # Sprawdź czy plik wykonywalny istnieje
    if not os.path.isfile(args.exe):
        print(f" BŁĄD: Plik wykonywalny '{args.exe}' nie istnieje!")
        sys.exit(1)
    
    # Konfiguracja testów
    config = {
        'exe_path': args.exe,
        'steps_list': args.steps,
        'max_threads': args.max_threads,
        'mode': args.mode,
        'repeats': args.repeats,
        'timeout': args.timeout
    }
    
    if args.chunk is not None:
        config['chunk'] = args.chunk
    
    # Uruchom testy
    results = run_benchmark_suite(config)
    
    if not results:
        print(" Brak wyników do zapisania!")
        sys.exit(1)
    
    # Zapisz wyniki
    df = save_results(results, args.out_csv)
    
    # Wygeneruj wykresy (jeśli nie pomijamy)
    if not args.skip_plot:
        plot_results(df, args.out_png)
    
    # Podsumowanie
    print("\n" + "="*60)
    print("  PODSUMOWANIE")
    print("="*60)
    print(f"Plik CSV: {args.out_csv}")
    if not args.skip_plot:
        print(f"Plik wykresu: {args.out_png}")
        print(f"Plik speedup: {args.out_png.replace('.png', '_speedup.png')}")
    
    # Statystyki
    print("\n STATYSTYKI:")
    for steps in sorted(df['steps'].unique()):
        subset = df[df['steps'] == steps]
        best = subset.loc[subset['time_median'].idxmin()]
        print(f"  {steps:,} interwałów:")
        print(f" Najszybszy: {best['time_median']:.2f}s przy {int(best['threads'])} wątkach")
        
        # Speedup
        single = subset[subset['threads'] == 1]['time_median'].values[0]
        speedup = single / best['time_median']
        print(f" Przyspieszenie: {speedup:.2f}x (idealnie: {int(best['threads'])})x")
        print(f" Wydajność: {speedup/int(best['threads'])*100:.1f}%")
    
    print("\n  Wszystko gotowe!")

if __name__ == '__main__':
    main()
