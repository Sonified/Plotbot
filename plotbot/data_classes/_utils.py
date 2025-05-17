# This file will contain utility functions for the data classes. 

import numpy as np
import pandas as pd

def _format_setattr_debug(name, value):
    """Helper function to create a concise debug string for __setattr__."""
    MAX_LEN = 100 # Max length for string representation
    msg = f"Setting attribute: {name}"
    if isinstance(value, (np.ndarray, pd.Series, pd.DataFrame)):
        dtype_str = f"dtype={getattr(value, 'dtype', 'N/A')}"
        shape_str = f"shape={getattr(value, 'shape', 'N/A')}"
        return f"{msg} (type={type(value).__name__}, {shape_str}, {dtype_str})"
    else:
        val_str = repr(value)
        if len(val_str) > MAX_LEN:
            val_str = val_str[:MAX_LEN] + '...'
        return f"{msg} with value: {val_str}" 