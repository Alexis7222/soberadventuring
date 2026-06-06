#!/usr/bin/env python3
"""Run the content agent on demand without waiting for Monday's schedule."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from main import main

if __name__ == "__main__":
    main()
