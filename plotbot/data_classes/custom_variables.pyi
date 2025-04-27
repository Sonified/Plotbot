# Stubs for plotbot.data_classes.custom_variables
# -*- coding: utf-8 -*-

import numpy as np
import types
from typing import Optional, List, Dict, Any

# Assume these types are defined elsewhere in plotbot and importable
from plotbot.plot_manager import plot_manager

# --- CustomVariablesContainer Class ---
class CustomVariablesContainer:
    # --- Public Attributes (with type hints) ---
    variables: Dict[str, plot_manager]
    sources: Dict[str, List[plot_manager]]
    operations: Dict[str, str]
    class_name: str

    # --- Methods ---
    def __init__(self) -> None: ...
    def get_subclass(self, subclass_name: str) -> Optional[plot_manager]: ...
    def register(self, name: str, variable: plot_manager, sources: List[plot_manager], operation: str) -> plot_manager: ...
    def update(self, name: str, trange: List[str]) -> Optional[plot_manager]: ...
    # Note: _make_globally_accessible is internal, omit from stub
    # def _make_globally_accessible(self, name: str, variable: plot_manager) -> None: ...


# --- Module-level Functions ---
def custom_variable(name: str, expression: plot_manager) -> plot_manager: ...

def test_custom_variables() -> bool: ...

# Reminder: If you add functions directly to the .py file (outside of classes), add their signatures here too, ending with '...'.
# Reminder: If you add classes directly to the .py file, add their signatures here too.
