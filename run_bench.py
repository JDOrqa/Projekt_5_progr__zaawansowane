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
