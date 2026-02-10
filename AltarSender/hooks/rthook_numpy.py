# Runtime hook to fix NumPy CPU dispatcher issue
# This runs BEFORE any imports happen

import os
import sys

# Prevent numpy from initializing CPU dispatcher twice
os.environ['NUMPY_MADVISE_HUGEPAGE'] = '0'
os.environ['NPY_DISABLE_CPU_FEATURES'] = ''

# Alternative fix: set this before numpy imports
if hasattr(sys, '_MEIPASS'):
    # Running in PyInstaller bundle
    os.environ['OPENBLAS_NUM_THREADS'] = '1'
    os.environ['MKL_NUM_THREADS'] = '1'

