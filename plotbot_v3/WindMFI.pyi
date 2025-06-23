# This is an auto-generated .pyi file. Do not edit manually.
import numpy as np
from collections import namedtuple

class SimplePlotManager:
    data: np.ndarray
    plot_options: dict
    datetime_array: np.ndarray | None
    name: str
    def __init__(self, data_array: np.ndarray, plot_options_dict: dict, datetime_array: np.ndarray | None = ..., /) -> None: ...
    def __repr__(self) -> str: ...

TestDataObject = namedtuple('TestDataObject', ['times', 'data'])
dummy_metadata: dict # Or more specific type if metadata structure is fixed

def create_data_class(class_name_str: str, metadata: dict) -> type[WindMFI]: ...

class WindMFI:
    _metadata: dict
    class_name: str
    data_type: str
    _raw_data_arrays: dict
    datetime_array: np.ndarray
    _plot_managers: dict

    bx_gse: SimplePlotManager
    by_gse: SimplePlotManager
    bz_gse: SimplePlotManager
    bmag: SimplePlotManager

    def __init__(self, imported_data_obj: TestDataObject | None = ..., /) -> None: ...
    def update(self, imported_data_obj: TestDataObject, /) -> None: ...
    def __dir__(self) -> list[str]: ...
