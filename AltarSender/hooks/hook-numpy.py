# PyInstaller hook for NumPy CPU dispatcher issue
import os
import sys

# Prevent numpy from initializing the CPU dispatcher twice
os.environ['NPY_DISABLE_CPU_FEATURES'] = ''

