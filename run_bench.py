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
