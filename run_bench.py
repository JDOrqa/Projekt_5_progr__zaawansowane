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
