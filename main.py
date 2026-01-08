#!/usr/bin/env python3
"""
NomNom - Insider Trading Signal Detection for Prediction Markets

Run directly: python main.py scan
Or install: pip install -e . && nomnom scan
"""

import sys
import os

# Add package to path for direct execution
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nomnom.cli import main

if __name__ == "__main__":
    main()
